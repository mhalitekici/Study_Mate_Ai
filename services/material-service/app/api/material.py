from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.minio_client import minio_client, ensure_buckets, HOT_BUCKET, COLD_BUCKET, move_to_cold_storage
from app.core.kafka_producer import publish_event
from app.models.material import Material
from app.schemas.material import MaterialResponse, MaterialListResponse
import httpx
import uuid
import io
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi

security = HTTPBearer()

router = APIRouter(prefix="/materials", tags=["materials"])

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.AUTH_SERVICE_URL}/auth/validate",
            params={"token": token}
        )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")
    return response.json()

@router.post("/upload", response_model=MaterialResponse, status_code=201)
async def upload_material(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    allowed_types = ["application/pdf", "text/plain",
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed. Use PDF, TXT or DOCX.")

    ensure_buckets()
    file_content = await file.read()
    file_size = len(file_content) / (1024 * 1024)

    if file_size > 50:
        raise HTTPException(status_code=400, detail="File too large. Max 50MB.")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    minio_path = f"user_{current_user['user_id']}/{unique_filename}"

    minio_client.put_object(
        HOT_BUCKET,
        minio_path,
        io.BytesIO(file_content),
        length=len(file_content),
        content_type=file.content_type
    )

    material = Material(
        user_id=current_user["user_id"],
        filename=unique_filename,
        original_filename=file.filename,
        file_type=file.content_type,
        file_size=file_size,
        minio_path=minio_path,
        status="uploaded",
        storage_tier="hot"
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    publish_event("material.uploaded", {
        "material_id": material.id,
        "user_id": material.user_id,
        "minio_path": minio_path,
        "file_type": file.content_type
    })

    return material

@router.get("/", response_model=MaterialListResponse)
async def list_materials(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    materials = db.query(Material).filter(
        Material.user_id == current_user["user_id"]
    ).all()
    return MaterialListResponse(materials=materials, total=len(materials))

@router.delete("/{material_id}", status_code=204)
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.user_id == current_user["user_id"]
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    bucket = COLD_BUCKET if material.storage_tier == "cold" else HOT_BUCKET
    minio_client.remove_object(bucket, material.minio_path)
    db.delete(material)
    db.commit()

@router.post("/archive/{material_id}")
async def archive_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Move old material to cold storage"""
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.user_id == current_user["user_id"]
    ).first()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    if material.storage_tier == "cold":
        raise HTTPException(status_code=400, detail="Material already in cold storage")

    move_to_cold_storage(material.minio_path)

    material.status = "archived"
    material.storage_tier = "cold"
    db.commit()

    return {
        "message": "Material moved to cold storage",
        "material_id": material_id,
        "storage_tier": "cold"
    }

@router.get("/storage/stats")
async def get_storage_stats():
    """Get hot vs cold storage statistics"""
    try:
        hot_objects = list(minio_client.list_objects(HOT_BUCKET))
        cold_objects = list(minio_client.list_objects(COLD_BUCKET))

        return {
            "hot_storage": {
                "bucket": HOT_BUCKET,
                "count": len(hot_objects),
                "description": "Active materials uploaded within last 30 days"
            },
            "cold_storage": {
                "bucket": COLD_BUCKET,
                "count": len(cold_objects),
                "description": "Archived materials older than 30 days"
            }
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/health")
def health():
    return {"status": "healthy", "service": "material-service"}
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.minio_client import minio_client, ensure_bucket
from app.core.kafka_producer import publish_event
from app.models.material import Material
from app.schemas.material import MaterialResponse, MaterialListResponse
import httpx
import uuid
import io

router = APIRouter(prefix="/materials", tags=["materials"])

async def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
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

    ensure_bucket()
    file_content = await file.read()
    file_size = len(file_content) / (1024 * 1024)

    if file_size > 50:
        raise HTTPException(status_code=400, detail="File too large. Max 50MB.")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    minio_path = f"user_{current_user['user_id']}/{unique_filename}"

    minio_client.put_object(
        settings.MINIO_BUCKET,
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
        status="uploaded"
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

    minio_client.remove_object(settings.MINIO_BUCKET, material.minio_path)
    db.delete(material)
    db.commit()

@router.get("/health")
def health():
    return {"status": "healthy", "service": "material-service"}
from minio import Minio
from minio.commonconfig import CopySource
from app.core.config import settings

minio_client = Minio(
    settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False
)

HOT_BUCKET = "hot-materials"
COLD_BUCKET = "cold-materials"

def ensure_buckets():
    for bucket in [HOT_BUCKET, COLD_BUCKET]:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
            print(f"[MinIO] Created bucket: {bucket}")

def get_bucket_for_file(days_old: int = 0) -> str:
    if days_old > 30:
        return COLD_BUCKET
    return HOT_BUCKET

def move_to_cold_storage(minio_path: str):
    try:
        minio_client.copy_object(
            COLD_BUCKET,
            minio_path,
            CopySource(HOT_BUCKET, minio_path)
        )
        minio_client.remove_object(HOT_BUCKET, minio_path)
        print(f"[MinIO] Moved to cold storage: {minio_path}")
    except Exception as e:
        print(f"[MinIO] Cold storage move error: {e}")
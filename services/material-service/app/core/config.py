from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MATERIAL_DB_URL: str
    MINIO_URL: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "study-materials"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:29092"
    AUTH_SERVICE_URL: str = "http://localhost:8081"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../../../../.env")
        extra = "ignore"

settings = Settings()
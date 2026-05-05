from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGODB_URL: str
    QDRANT_URL: str = "http://localhost:6333"
    COLLECTION_NAME: str = "study_materials"
    AUTH_SERVICE_URL: str = "http://localhost:8081"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../../../../.env")
        extra = "ignore"

settings = Settings()
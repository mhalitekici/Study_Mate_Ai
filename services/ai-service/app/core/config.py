from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    QDRANT_URL: str = "http://localhost:6333"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5"
    MEMORY_SERVICE_URL: str = "http://localhost:8084"
    AUTH_SERVICE_URL: str = "http://localhost:8081"
    LANGFUSE_PUBLIC_KEY: str = "pk-lf-placeholder"
    LANGFUSE_SECRET_KEY: str = "sk-lf-placeholder"
    LANGFUSE_HOST: str = "http://localhost:3001"
    COLLECTION_NAME: str = "study_materials"
    REDIS_URL: str = "redis://localhost:6379"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:29092"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../../../../.env")
        extra = "ignore"

settings = Settings()
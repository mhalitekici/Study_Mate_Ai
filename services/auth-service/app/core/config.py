from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    AUTH_DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:29092"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../../../../.env")
        extra = "ignore"

settings = Settings()
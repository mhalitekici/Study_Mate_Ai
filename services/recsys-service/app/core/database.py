import motor.motor_asyncio
from app.core.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
db = client.recsys_db

interactions_collection = db.interactions
recommendations_collection = db.recommendations
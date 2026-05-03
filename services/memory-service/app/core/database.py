import motor.motor_asyncio
from app.core.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
db = client.memory_db

conversations_collection = db.conversations
summaries_collection = db.summaries
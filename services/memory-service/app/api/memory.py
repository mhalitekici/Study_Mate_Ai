from fastapi import APIRouter, HTTPException, Header
from app.core.database import conversations_collection
from app.core.config import settings
from app.schemas.memory import MessageCreate, MessageResponse, ConversationHistory
import httpx
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/memory", tags=["memory"])

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

def serialize_message(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "user_id": doc["user_id"],
        "question": doc["question"],
        "answer": doc["answer"],
        "material_ids": doc.get("material_ids", []),
        "created_at": doc["created_at"]
    }

@router.post("/save", status_code=201)
async def save_message(message: MessageCreate):
    doc = {
        "user_id": message.user_id,
        "question": message.question,
        "answer": message.answer,
        "material_ids": message.material_ids,
        "created_at": datetime.utcnow()
    }
    result = await conversations_collection.insert_one(doc)
    return {"id": str(result.inserted_id), "status": "saved"}

@router.get("/history/{user_id}")
async def get_history(user_id: int, limit: int = 10):
    cursor = conversations_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit)

    messages = []
    async for doc in cursor:
        messages.append(serialize_message(doc))

    messages.reverse()
    return ConversationHistory(
        user_id=user_id,
        messages=messages,
        total=len(messages)
    )

@router.get("/context/{user_id}")
async def get_context(user_id: int, limit: int = 5):
    cursor = conversations_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit)

    context = []
    async for doc in cursor:
        context.append({
            "role": "user",
            "content": doc["question"]
        })
        context.append({
            "role": "assistant",
            "content": doc["answer"]
        })

    context.reverse()
    return {"user_id": user_id, "context": context}

@router.delete("/history/{user_id}", status_code=204)
async def clear_history(user_id: int):
    await conversations_collection.delete_many({"user_id": user_id})

@router.get("/health")
def health():
    return {"status": "healthy", "service": "memory-service"}
from fastapi import APIRouter, Header, HTTPException
from app.core.content_based import content_based_recommend
from app.core.collaborative import collaborative_recommend, log_interaction
from app.core.heuristic import heuristic_recommend, cold_start_recommend
from pydantic import BaseModel
from typing import Optional
import httpx
from app.core.config import settings

router = APIRouter(prefix="/recsys", tags=["recsys"])

class RecommendRequest(BaseModel):
    user_id: int
    current_question: Optional[str] = None
    top_k: int = 5

class LogInteractionRequest(BaseModel):
    user_id: int
    question: str

@router.post("/recommend")
async def get_recommendations(request: RecommendRequest):
    recommendations = {
        "user_id": request.user_id,
        "content_based": [],
        "collaborative": [],
        "heuristic": [],
        "cold_start": []
    }

    # Content-based — eğer soru varsa
    if request.current_question:
        recommendations["content_based"] = await content_based_recommend(
            request.user_id,
            request.current_question,
            request.top_k
        )

    # Collaborative
    collab = await collaborative_recommend(request.user_id, request.top_k)
    recommendations["collaborative"] = collab

    # Heuristic
    heuristic = await heuristic_recommend(request.user_id, request.top_k)
    recommendations["heuristic"] = heuristic

    # Cold start — eğer hiç öneri yoksa
    if not collab and not heuristic:
        recommendations["cold_start"] = await cold_start_recommend()

    return recommendations

@router.post("/log", status_code=201)
async def log_user_interaction(request: LogInteractionRequest):
    await log_interaction(request.user_id, request.question)
    return {"status": "logged", "user_id": request.user_id}

@router.get("/popular")
async def get_popular_topics():
    return await heuristic_recommend(user_id=0, top_k=10)

@router.get("/health")
def health():
    return {"status": "healthy", "service": "recsys-service"}
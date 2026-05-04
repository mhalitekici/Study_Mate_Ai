from fastapi import APIRouter, HTTPException, Header
from app.core.config import settings
from app.core.rag_pipeline import retrieve_context, generate_answer
from app.core.qdrant_client import qdrant, ensure_collection
from app.core.cache import get_cached_answer, set_cached_answer
from app.schemas.ai import QuestionRequest, AnswerResponse, IndexRequest
from qdrant_client.models import PointStruct
import httpx
import uuid

router = APIRouter(tags=["ai"])

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

async def get_conversation_history(user_id: int) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{settings.MEMORY_SERVICE_URL}/memory/context/{user_id}"
            )
            if response.status_code == 200:
                return response.json().get("context", [])
    except Exception:
        pass
    return []

async def save_to_memory(user_id: int, question: str, answer: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{settings.MEMORY_SERVICE_URL}/memory/save",
                json={
                    "user_id": user_id,
                    "question": question,
                    "answer": answer,
                    "material_ids": []
                }
            )
    except Exception:
        pass

@router.post("/generate", response_model=AnswerResponse)
async def generate(request: QuestionRequest):
    # Redis cache kontrolü
    cached = get_cached_answer(request.question, request.user_id)
    if cached:
        return AnswerResponse(**cached)

    try:
        from app.core.langfuse_client import langfuse
        trace = langfuse.trace(
            name="study-mate-ai-query",
            user_id=str(request.user_id),
            input=request.question
        )
    except Exception:
        trace = None

    history = await get_conversation_history(request.user_id)
    context = await retrieve_context(request.question, request.user_id)
    context_used = context != "No relevant context found in uploaded materials."

    answer = await generate_answer(request.question, context, history, trace)

    await save_to_memory(request.user_id, request.question, answer)

    result = {
        "question": request.question,
        "answer": answer,
        "context_used": context_used,
        "user_id": request.user_id
    }

    # Redis'e cache'le
    set_cached_answer(request.question, request.user_id, result)

    if trace:
        trace.update(output=answer)

    return AnswerResponse(**result)

@router.post("/index", status_code=201)
async def index_material(request: IndexRequest):
    ensure_collection()
    return {"status": "indexing_started", "material_id": request.material_id}

@router.get("/health")
def health():
    return {"status": "healthy", "service": "ai-service"}
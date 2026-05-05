from fastapi import APIRouter, HTTPException
from app.core.graph import agent_graph
from app.core.config import settings
from app.core.state import AgentState
from app.core.cache import get_cached_answer, set_cached_answer
from pydantic import BaseModel
import httpx

router = APIRouter(prefix="/agent", tags=["agent"])

class AgentRequest(BaseModel):
    question: str
    user_id: int

class AgentResponse(BaseModel):
    question: str
    answer: str
    evaluation_score: float
    evaluation_feedback: str
    user_id: int
    cached: bool = False

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

@router.post("/ask", response_model=AgentResponse)
async def ask_agent(request: AgentRequest):

    # Redis cache kontrolü
    cached = get_cached_answer(request.question, request.user_id)
    if cached:
        print(f"[Agent] Returning cached answer")
        cached_data = {k: v for k, v in cached.items() if k != 'cached'}
        return AgentResponse(**cached_data, cached=True)

    try:
        from app.core.langfuse_client import langfuse
        trace = langfuse.trace(
            name="multi-agent-query",
            user_id=str(request.user_id),
            input=request.question
        )
    except Exception:
        trace = None

    initial_state: AgentState = {
        "user_id": request.user_id,
        "question": request.question,
        "context": "",
        "history": [],
        "answer": "",
        "evaluation_score": 0.0,
        "evaluation_feedback": "",
        "needs_retry": False,
        "error": None
    }

    try:
        final_state = await agent_graph.ainvoke(initial_state)
        answer = final_state["answer"]

        # Eğer cevap boşsa bir kez daha dene
        if not answer or len(answer) < 10:
            print("[Agent] Empty answer, retrying...")
            final_state = await agent_graph.ainvoke(initial_state)
            answer = final_state["answer"]

        if answer and len(answer) > 10:
            await save_to_memory(request.user_id, request.question, answer)

            result = {
                "question": request.question,
                "answer": answer,
                "evaluation_score": final_state["evaluation_score"],
                "evaluation_feedback": final_state["evaluation_feedback"],
                "user_id": request.user_id,
                "cached": False
            }

            set_cached_answer(request.question, request.user_id, result)

            if trace:
                trace.update(output=answer)

            return AgentResponse(**result)
        else:
            raise HTTPException(status_code=500, detail="Failed to generate answer after retry")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health():
    return {"status": "healthy", "service": "multi-agent"}
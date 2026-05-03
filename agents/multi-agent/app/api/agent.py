from fastapi import APIRouter, HTTPException, Header
from app.core.graph import agent_graph
from app.core.config import settings
from app.core.state import AgentState
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
        await save_to_memory(
            request.user_id,
            request.question,
            final_state["answer"]
        )

        if trace:
            trace.update(output=final_state["answer"])

        return AgentResponse(
            question=request.question,
            answer=final_state["answer"],
            evaluation_score=final_state["evaluation_score"],
            evaluation_feedback=final_state["evaluation_feedback"],
            user_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health():
    return {"status": "healthy", "service": "multi-agent"}
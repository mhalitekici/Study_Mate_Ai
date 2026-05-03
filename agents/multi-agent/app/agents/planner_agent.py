from app.core.state import AgentState
from app.core.config import settings
import httpx

async def get_history(user_id: int) -> list[dict]:
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

async def planner_agent(state: AgentState) -> AgentState:
    print(f"[Planner Agent] Planning for question: {state['question'][:50]}...")
    
    history = await get_history(state["user_id"])
    print(f"[Planner Agent] Retrieved {len(history)} history messages")
    
    return {
        **state,
        "history": history,
        "context": "",
        "answer": "",
        "evaluation_score": 0.0,
        "evaluation_feedback": "",
        "needs_retry": False,
        "error": None
    }
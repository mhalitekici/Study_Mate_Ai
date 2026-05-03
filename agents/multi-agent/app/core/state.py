from typing import TypedDict, Optional

class AgentState(TypedDict):
    user_id: int
    question: str
    context: str
    history: list[dict]
    answer: str
    evaluation_score: float
    evaluation_feedback: str
    needs_retry: bool
    error: Optional[str]
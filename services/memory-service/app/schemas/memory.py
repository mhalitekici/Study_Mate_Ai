from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    user_id: int
    question: str
    answer: str
    material_ids: Optional[list[int]] = []

class MessageResponse(BaseModel):
    id: str
    user_id: int
    question: str
    answer: str
    material_ids: list[int]
    created_at: datetime

class ConversationHistory(BaseModel):
    user_id: int
    messages: list[MessageResponse]
    total: int
from pydantic import BaseModel
from typing import Optional

class QuestionRequest(BaseModel):
    question: str
    user_id: int
    material_ids: Optional[list[int]] = []

class AnswerResponse(BaseModel):
    question: str
    answer: str
    context_used: bool
    user_id: int

class IndexRequest(BaseModel):
    material_id: int
    user_id: int
    minio_path: str
    file_type: str
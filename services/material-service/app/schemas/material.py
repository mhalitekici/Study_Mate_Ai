from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MaterialResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class MaterialListResponse(BaseModel):
    materials: list[MaterialResponse]
    total: int
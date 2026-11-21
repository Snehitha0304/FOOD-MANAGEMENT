from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    restaurant_rating: int = Field(..., ge=1, le=5)
    agent_rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)


class RatingResponse(BaseModel):
    id: int
    order_id: int
    restaurant_rating: int
    agent_rating: int
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

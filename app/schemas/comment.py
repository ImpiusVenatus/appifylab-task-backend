import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.post import PostAuthorResponse


class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    parent_id: uuid.UUID | None = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    parent_id: uuid.UUID | None
    content: str
    created_at: datetime
    updated_at: datetime
    author: PostAuthorResponse
    like_count: int = 0
    liked_by_me: bool = False
    replies: list["CommentResponse"] = []

    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int

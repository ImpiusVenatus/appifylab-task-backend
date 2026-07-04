import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import PostVisibility


class PostAuthorResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: uuid.UUID
    content: str
    image_url: str | None
    visibility: PostVisibility
    created_at: datetime
    updated_at: datetime
    author: PostAuthorResponse
    like_count: int = 0
    comment_count: int = 0
    liked_by_me: bool = False

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

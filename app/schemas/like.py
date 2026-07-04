import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import LikeTargetType
from app.schemas.post import PostAuthorResponse


class LikeRequest(BaseModel):
    target_type: LikeTargetType
    target_id: uuid.UUID


class LikeResponse(BaseModel):
    target_type: LikeTargetType
    target_id: uuid.UUID
    liked: bool


class LikeUserResponse(BaseModel):
    user: PostAuthorResponse
    liked_at: datetime

    model_config = {"from_attributes": True}


class LikeListResponse(BaseModel):
    items: list[LikeUserResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

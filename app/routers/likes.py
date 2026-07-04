import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.enums import LikeTargetType
from app.models.like import Like
from app.models.user import User
from app.schemas.like import LikeListResponse, LikeRequest, LikeResponse, LikeUserResponse
from app.schemas.post import PostAuthorResponse
from app.services.access import verify_like_target

router = APIRouter(prefix="/likes", tags=["likes"])

DEFAULT_LIMIT = 20
MAX_LIMIT = 50


@router.post("", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
def like_target(
    body: LikeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LikeResponse:
    verify_like_target(body.target_type, body.target_id, current_user, db)

    existing = db.scalar(
        select(Like).where(
            Like.user_id == current_user.id,
            Like.target_type == body.target_type.value,
            Like.target_id == body.target_id,
        )
    )
    if existing:
        return LikeResponse(
            target_type=body.target_type,
            target_id=body.target_id,
            liked=True,
        )

    like = Like(
        user_id=current_user.id,
        target_type=body.target_type.value,
        target_id=body.target_id,
    )
    db.add(like)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return LikeResponse(
            target_type=body.target_type,
            target_id=body.target_id,
            liked=True,
        )

    return LikeResponse(
        target_type=body.target_type,
        target_id=body.target_id,
        liked=True,
    )


@router.delete("", response_model=LikeResponse)
def unlike_target(
    body: LikeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LikeResponse:
    verify_like_target(body.target_type, body.target_id, current_user, db)

    like = db.scalar(
        select(Like).where(
            Like.user_id == current_user.id,
            Like.target_type == body.target_type.value,
            Like.target_id == body.target_id,
        )
    )
    if like:
        db.delete(like)
        db.commit()

    return LikeResponse(
        target_type=body.target_type,
        target_id=body.target_id,
        liked=False,
    )


@router.get("", response_model=LikeListResponse)
def list_likes(
    target_type: LikeTargetType = Query(),
    target_id: uuid.UUID = Query(),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LikeListResponse:
    verify_like_target(target_type, target_id, current_user, db)

    base_filter = (
        Like.target_type == target_type.value,
        Like.target_id == target_id,
    )

    total = db.scalar(select(func.count()).select_from(Like).where(*base_filter)) or 0

    rows = db.execute(
        select(Like, User)
        .join(User, User.id == Like.user_id)
        .where(*base_filter)
        .order_by(Like.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    items = [
        LikeUserResponse(
            user=PostAuthorResponse.model_validate(user),
            liked_at=like.created_at,
        )
        for like, user in rows
    ]

    return LikeListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(items) < total,
    )

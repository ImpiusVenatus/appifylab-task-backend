import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import LikeTargetType
from app.models.like import Like
from app.models.user import User


def get_like_counts(
    db: Session,
    target_type: LikeTargetType,
    target_ids: list[uuid.UUID],
) -> dict[uuid.UUID, int]:
    if not target_ids:
        return {}

    return dict(
        db.execute(
            select(Like.target_id, func.count())
            .where(
                Like.target_type == target_type.value,
                Like.target_id.in_(target_ids),
            )
            .group_by(Like.target_id)
        ).all()
    )


def get_liked_by_me(
    db: Session,
    target_type: LikeTargetType,
    target_ids: list[uuid.UUID],
    user_id: uuid.UUID,
) -> set[uuid.UUID]:
    if not target_ids:
        return set()

    return set(
        db.scalars(
            select(Like.target_id).where(
                Like.user_id == user_id,
                Like.target_type == target_type.value,
                Like.target_id.in_(target_ids),
            )
        ).all()
    )

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.enums import LikeTargetType, PostVisibility
from app.models.like import Like
from app.models.post import Post
from app.models.user import User


def get_visible_post(post_id: uuid.UUID, current_user: User, db: Session) -> Post:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.visibility == PostVisibility.PRIVATE.value and post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return post


def get_visible_comment(comment_id: uuid.UUID, current_user: User, db: Session) -> Comment:
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    get_visible_post(comment.post_id, current_user, db)
    return comment


def verify_like_target(target_type: LikeTargetType, target_id: uuid.UUID, current_user: User, db: Session) -> None:
    if target_type == LikeTargetType.POST:
        get_visible_post(target_id, current_user, db)
        return

    if target_type == LikeTargetType.COMMENT:
        get_visible_comment(target_id, current_user, db)
        return

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid like target type")

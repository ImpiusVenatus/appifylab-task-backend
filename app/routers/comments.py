import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.comment import Comment
from app.models.enums import LikeTargetType
from app.models.user import User
from app.schemas.comment import CommentCreateRequest, CommentListResponse, CommentResponse
from app.services.access import get_visible_post
from app.services.likes import get_like_counts, get_liked_by_me

router = APIRouter(tags=["comments"])


def _build_comment_tree(
    comments: list[Comment],
    like_counts: dict[uuid.UUID, int],
    liked_ids: set[uuid.UUID],
) -> list[CommentResponse]:
    nodes: dict[uuid.UUID, CommentResponse] = {}

    for comment in comments:
        nodes[comment.id] = CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            content=comment.content,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            author=comment.author,
            like_count=like_counts.get(comment.id, 0),
            liked_by_me=comment.id in liked_ids,
            replies=[],
        )

    roots: list[CommentResponse] = []
    for comment in comments:
        node = nodes[comment.id]
        if comment.parent_id is None:
            roots.append(node)
        else:
            parent = nodes.get(comment.parent_id)
            if parent is not None:
                parent.replies.append(node)

    return roots


@router.get("/{post_id}/comments", response_model=CommentListResponse)
def list_comments(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentListResponse:
    get_visible_post(post_id, current_user, db)

    comments = db.scalars(
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    ).all()

    comment_ids = [comment.id for comment in comments]
    like_counts = get_like_counts(db, LikeTargetType.COMMENT, comment_ids)
    liked_ids = get_liked_by_me(db, LikeTargetType.COMMENT, comment_ids, current_user.id)

    items = _build_comment_tree(comments, like_counts, liked_ids)
    return CommentListResponse(items=items, total=len(comments))


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: uuid.UUID,
    body: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    get_visible_post(post_id, current_user, db)

    parent_id = body.parent_id
    if parent_id is not None:
        parent = db.get(Comment, parent_id)
        if not parent or parent.post_id != post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment not found on this post",
            )

    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        parent_id=parent_id,
        content=body.content.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        author=comment.author,
        like_count=0,
        liked_by_me=False,
        replies=[],
    )

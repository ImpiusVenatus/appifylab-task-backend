import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.deps import get_current_user
from app.models.comment import Comment
from app.models.enums import LikeTargetType, PostVisibility
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostListResponse, PostResponse
from app.services.cloudinary import delete_post_image, upload_post_image
from app.services.likes import get_like_counts, get_liked_by_me

router = APIRouter(tags=["posts"])

DEFAULT_LIMIT = 20
MAX_LIMIT = 50
MAX_POST_CONTENT_LENGTH = 5000


def _build_post_response(post: Post, like_count: int, comment_count: int, liked_by_me: bool) -> PostResponse:
    return PostResponse(
        id=post.id,
        content=post.content,
        image_url=post.image_url,
        visibility=PostVisibility(post.visibility),
        created_at=post.created_at,
        updated_at=post.updated_at,
        author=post.author,
        like_count=like_count,
        comment_count=comment_count,
        liked_by_me=liked_by_me,
    )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    content: Annotated[str, Form()] = "",
    visibility: Annotated[PostVisibility, Form()] = PostVisibility.PUBLIC,
    image: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> PostResponse:
    trimmed_content = content.strip()
    has_image = image is not None and image.filename

    if not trimmed_content and not has_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post must include text, an image, or both.",
        )

    if len(trimmed_content) > MAX_POST_CONTENT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post text must be {MAX_POST_CONTENT_LENGTH} characters or fewer.",
        )

    image_url: str | None = None
    image_public_id: str | None = None

    if has_image and image is not None:
        uploaded = await upload_post_image(image, settings)
        image_url = uploaded.url
        image_public_id = uploaded.public_id

    post = Post(
        author_id=current_user.id,
        content=trimmed_content,
        image_url=image_url,
        image_public_id=image_public_id,
        visibility=visibility.value,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return _build_post_response(post, like_count=0, comment_count=0, liked_by_me=False)


@router.get("", response_model=PostListResponse)
def list_posts(
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostListResponse:
    visibility_filter = or_(
        Post.visibility == PostVisibility.PUBLIC.value,
        Post.author_id == current_user.id,
    )

    posts = db.scalars(
        select(Post)
        .where(visibility_filter)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    if not posts:
        return PostListResponse(
            items=[],
            total=0,
            limit=limit,
            offset=offset,
            has_more=False,
        )

    post_ids = [post.id for post in posts]

    like_counts = get_like_counts(db, LikeTargetType.POST, post_ids)
    my_likes = get_liked_by_me(db, LikeTargetType.POST, post_ids, current_user.id)

    comment_counts = dict(
        db.execute(
            select(Comment.post_id, func.count())
            .where(Comment.post_id.in_(post_ids))
            .group_by(Comment.post_id)
        ).all()
    )

    items = [
        _build_post_response(
            post,
            like_count=like_counts.get(post.id, 0),
            comment_count=comment_counts.get(post.id, 0),
            liked_by_me=post.id in my_likes,
        )
        for post in posts
    ]

    return PostListResponse(
        items=items,
        total=offset + len(items),
        limit=limit,
        offset=offset,
        has_more=len(items) == limit,
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> None:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts.",
        )

    if post.image_public_id:
        delete_post_image(post.image_public_id, settings)

    db.delete(post)
    db.commit()

from dataclasses import dataclass

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.config import Settings

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


@dataclass(frozen=True)
class UploadedImage:
    url: str
    public_id: str


def configure_cloudinary(settings: Settings) -> None:
    if not settings.cloudinary_cloud_name:
        return

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def ensure_cloudinary_configured(settings: Settings) -> None:
    if not settings.cloudinary_cloud_name or not settings.cloudinary_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image uploads are not configured. Set Cloudinary environment variables.",
        )
    configure_cloudinary(settings)


async def upload_post_image(file: UploadFile, settings: Settings) -> UploadedImage:
    ensure_cloudinary_configured(settings)

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image type. Use JPEG, PNG, WebP, or GIF.",
        )

    contents = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image must be {settings.max_upload_size_mb}MB or smaller.",
        )

    try:
        result = cloudinary.uploader.upload(
            contents,
            folder=settings.cloudinary_folder,
            resource_type="image",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload image to Cloudinary.",
        ) from exc

    return UploadedImage(url=result["secure_url"], public_id=result["public_id"])


async def upload_user_avatar(file: UploadFile, settings: Settings) -> UploadedImage:
    ensure_cloudinary_configured(settings)

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image type. Use JPEG, PNG, WebP, or GIF.",
        )

    contents = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image must be {settings.max_upload_size_mb}MB or smaller.",
        )

    try:
        result = cloudinary.uploader.upload(
            contents,
            folder=f"{settings.cloudinary_folder.rsplit('/', 1)[0]}/avatars",
            resource_type="image",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to upload avatar to Cloudinary.",
        ) from exc

    return UploadedImage(url=result["secure_url"], public_id=result["public_id"])


def delete_cloudinary_image(public_id: str, settings: Settings) -> None:
    if not public_id:
        return

    ensure_cloudinary_configured(settings)

    try:
        cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to delete image from Cloudinary.",
        ) from exc


def delete_post_image(public_id: str, settings: Settings) -> None:
    delete_cloudinary_image(public_id, settings)

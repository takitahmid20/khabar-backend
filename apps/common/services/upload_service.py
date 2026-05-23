from django.core.files.uploadedfile import UploadedFile

from apps.common.models.asset import Asset
from apps.users.models import User
from core.exceptions import ServiceException

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
]


class UploadService:
    @staticmethod
    def upload_file(user: User, file: UploadedFile, purpose: str) -> Asset:
        # Validate purpose
        valid_purposes = [choice[0] for choice in Asset.Purpose.choices]
        if purpose not in valid_purposes:
            raise ServiceException(
                code="INVALID_PURPOSE",
                message=f"Invalid upload purpose. Must be one of: {', '.join(valid_purposes)}.",
            )

        # Validate file size
        if file.size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE // (1024 * 1024)
            raise ServiceException(
                code="FILE_TOO_LARGE",
                message=f"File is too large. Maximum size is {max_mb} MB.",
            )

        # Validate mime type for image purposes
        content_type = file.content_type or ""
        image_purposes = [
            Asset.Purpose.AVATAR,
            Asset.Purpose.KITCHEN_PHOTO,
            Asset.Purpose.NID_FRONT,
            Asset.Purpose.NID_BACK,
            Asset.Purpose.SELFIE,
            Asset.Purpose.MENU_ITEM,
        ]
        if purpose in image_purposes and content_type not in ALLOWED_IMAGE_TYPES:
            raise ServiceException(
                code="INVALID_FILE_TYPE",
                message="Please upload a valid image (JPEG, PNG, or WebP).",
            )

        asset = Asset.objects.create(
            user=user,
            file=file,
            purpose=purpose,
            mime_type=content_type,
            file_size=file.size,
            original_filename=file.name or "",
        )

        return asset

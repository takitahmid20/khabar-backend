import uuid

from django.db import models

from core.models import BaseModel


def asset_upload_path(instance, filename):
    """Generate upload path: assets/<purpose>/<uuid>/<filename>"""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return f"assets/{instance.purpose}/{unique_name}"


class Asset(BaseModel):
    class Purpose(models.TextChoices):
        AVATAR = "avatar", "Avatar"
        KITCHEN_PHOTO = "kitchen_photo", "Kitchen Photo"
        NID_FRONT = "nid_front", "NID Front"
        NID_BACK = "nid_back", "NID Back"
        SELFIE = "selfie", "Selfie"
        MENU_ITEM = "menu_item", "Menu Item"
        GENERAL = "general", "General"

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="assets",
    )
    file = models.FileField(upload_to=asset_upload_path)
    purpose = models.CharField(max_length=30, choices=Purpose.choices, default=Purpose.GENERAL)
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    original_filename = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.purpose} - {self.original_filename}"

    @property
    def url(self):
        if self.file:
            return self.file.url
        return None

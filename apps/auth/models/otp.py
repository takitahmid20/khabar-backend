from django.db import models
from django.utils import timezone

from core.models import BaseModel
from shared.enums.core import UserRole


class OTP(BaseModel):
    class Method(models.TextChoices):
        MOBILE = "mobile", "Mobile"
        EMAIL = "email", "Email"

    method = models.CharField(max_length=10, choices=Method.choices)
    destination = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

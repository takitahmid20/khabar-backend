from django.db import models

from core.models import BaseModel
from shared.enums.core import VerificationStatus


class CookVerification(BaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="cook_verification")
    nid_front = models.FileField(upload_to="verification/nid_front/", null=True, blank=True)
    nid_back = models.FileField(upload_to="verification/nid_back/", null=True, blank=True)
    selfie = models.FileField(upload_to="verification/selfie/", null=True, blank=True)
    status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
    )

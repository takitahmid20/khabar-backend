from django.db import models

from core.models import BaseModel


class UserProfile(BaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="profile")
    metadata = models.JSONField(default=dict, blank=True)

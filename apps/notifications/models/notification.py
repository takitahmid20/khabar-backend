from django.db import models

from core.models import BaseModel


class Notification(BaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="notifications")
    event_key = models.CharField(max_length=120)
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)

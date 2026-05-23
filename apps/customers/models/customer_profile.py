from django.db import models

from core.models import BaseModel


class CustomerProfile(BaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="customer_profile")

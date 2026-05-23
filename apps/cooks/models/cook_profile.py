from django.contrib.postgres.fields import ArrayField
from django.db import models

from core.models import BaseModel
from shared.enums.core import PaymentMethod


class CookProfile(BaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="cook_profile")
    bio = models.TextField(null=True, blank=True)
    cuisine_types = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    specialties = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    capacity_per_day = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Meals per day capacity")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    total_orders_count = models.PositiveIntegerField(default=0)
    area_label = models.CharField(max_length=120, null=True, blank=True)
    radius_km = models.PositiveSmallIntegerField(null=True, blank=True)
    coordinates = models.JSONField(null=True, blank=True)
    holiday_mode_enabled = models.BooleanField(default=False)
    payout_method = models.CharField(max_length=20, choices=PaymentMethod.choices, null=True, blank=True)
    payout_number = models.CharField(max_length=30, null=True, blank=True)
    payout_account_name = models.CharField(max_length=120, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

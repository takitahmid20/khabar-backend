from django.db import models

from core.models import BaseModel
from shared.enums.core import DemandStatus


class DemandItem(BaseModel):
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE, related_name="demand_items")
    dish = models.ForeignKey("menu.Dish", on_delete=models.PROTECT)
    dish_name = models.CharField(max_length=120)
    meal_slot = models.CharField(max_length=20)
    date = models.DateField()
    cutoff_time = models.TimeField()
    baseline = models.PositiveIntegerField(default=0)
    one_off = models.PositiveIntegerField(default=0)
    overrides = models.PositiveIntegerField(default=0)
    cancellations = models.PositiveIntegerField(default=0)
    capacity = models.PositiveIntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    production_status = models.CharField(max_length=30, choices=DemandStatus.choices, default=DemandStatus.PENDING)

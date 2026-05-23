from django.contrib.postgres.fields import ArrayField
from django.db import models

from core.models import BaseModel
from shared.enums.core import DayKey, MealSlot


class Dish(BaseModel):
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField(max_length=120)
    description = models.TextField()
    category = models.CharField(max_length=60)
    meal_slot = models.CharField(max_length=20, choices=MealSlot.choices)
    days = ArrayField(models.CharField(max_length=3, choices=DayKey.choices), default=list)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=0)
    cutoff_time = models.TimeField()
    image_url = models.URLField(null=True, blank=True)
    add_ons_label = models.CharField(max_length=120, null=True, blank=True)
    available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)

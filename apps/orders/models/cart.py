from django.db import models

from core.models import BaseModel
from shared.enums.core import PlanType


class CartItem(BaseModel):
    customer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="cart_items")
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE)
    dish = models.ForeignKey("menu.Dish", on_delete=models.CASCADE)
    dish_name = models.CharField(max_length=120)
    meal_slot = models.CharField(max_length=20)
    day_label = models.CharField(max_length=20)
    plan_type = models.CharField(max_length=20, choices=PlanType.choices)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    month_multiplier = models.PositiveIntegerField(default=1)

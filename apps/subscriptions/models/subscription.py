from django.db import models

from core.models import BaseModel
from shared.enums.core import SubscriptionStatus


class Subscription(BaseModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="subscriptions")
    customer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="subscriptions")
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE, related_name="subscriptions")
    dish = models.ForeignKey("menu.Dish", on_delete=models.PROTECT)
    plan_name = models.CharField(max_length=120)
    meal_slot = models.CharField(max_length=20)
    portions_per_day = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE)
    paused_until = models.DateTimeField(null=True, blank=True)
    paused_portions = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()

from django.db import models

from core.models import BaseModel


class OrderItem(BaseModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey("menu.Dish", on_delete=models.PROTECT)
    dish_name = models.CharField(max_length=120)
    meal_slot = models.CharField(max_length=20)
    day_label = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    month_multiplier = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

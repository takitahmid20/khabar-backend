from django.db import models

from core.models import BaseModel


class OrderDelivery(BaseModel):
    """Tracks per-customer delivery status for today's orders."""
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="deliveries")
    dish_key = models.CharField(max_length=200, help_text="dishId::mealSlot composite key")
    date = models.DateField()
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("order", "dish_key", "date")]

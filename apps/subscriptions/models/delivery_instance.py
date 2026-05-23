from django.db import models

from core.models import BaseModel
from shared.enums.core import DeliveryStatus


class DeliveryInstance(BaseModel):
    subscription = models.ForeignKey("subscriptions.Subscription", on_delete=models.CASCADE, related_name="deliveries")
    customer = models.ForeignKey("users.User", on_delete=models.CASCADE)
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=30, choices=DeliveryStatus.choices, default=DeliveryStatus.SCHEDULED)
    quantity_ordered = models.PositiveIntegerField(default=1)
    quantity_delivered = models.PositiveIntegerField(default=0)
    quantity_skipped = models.PositiveIntegerField(default=0)
    delivered_at = models.DateTimeField(null=True, blank=True)
    skipped_at = models.DateTimeField(null=True, blank=True)
    undoable_until = models.DateTimeField(null=True, blank=True)

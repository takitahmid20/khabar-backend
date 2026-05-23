from django.db import models

from core.models import BaseModel
from shared.enums.core import PaymentMethod, PaymentStatus


class Payment(BaseModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = models.CharField(max_length=120, null=True, blank=True)
    provider = models.CharField(max_length=50, null=True, blank=True)
    provider_payload = models.JSONField(default=dict, blank=True)

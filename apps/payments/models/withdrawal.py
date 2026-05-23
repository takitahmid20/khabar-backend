from django.db import models

from core.models import BaseModel
from shared.enums.core import PaymentMethod, WithdrawalStatus


class Withdrawal(BaseModel):
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE, related_name="withdrawals")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payout_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payout_number = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=WithdrawalStatus.choices, default=WithdrawalStatus.PROCESSING)
    processed_at = models.DateTimeField(null=True, blank=True)

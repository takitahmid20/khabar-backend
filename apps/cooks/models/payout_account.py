from django.db import models

from core.models import BaseModel
from shared.enums.core import PaymentMethod


class PayoutAccount(BaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="payout_account")
    payout_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payout_number = models.CharField(max_length=30)
    payout_account_name = models.CharField(max_length=120)
    is_default = models.BooleanField(default=True)

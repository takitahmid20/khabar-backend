from django.db import models

from core.models import BaseModel
from shared.enums.core import OrderStatus, PaymentMethod, PaymentStatus, PlanType


class Order(BaseModel):
    customer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="orders")
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE, related_name="orders")
    plan_type = models.CharField(max_length=20, choices=PlanType.choices)
    delivery_address = models.ForeignKey("locations.Address", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    promo_code = models.CharField(max_length=30, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    promo_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=OrderStatus.choices, default=OrderStatus.PENDING_PAYMENT)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)

from django.db import models

from core.models import BaseModel


class DemandContribution(BaseModel):
    demand_item = models.ForeignKey("orders.DemandItem", on_delete=models.CASCADE, related_name="contributions")
    customer = models.ForeignKey("users.User", on_delete=models.PROTECT)
    order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=120)
    company_name = models.CharField(max_length=120, null=True, blank=True)
    delivery_address = models.TextField()
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    type = models.CharField(max_length=30)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)

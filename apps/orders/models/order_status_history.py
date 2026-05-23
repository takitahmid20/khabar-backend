from django.db import models

from core.models import BaseModel


class OrderStatusHistory(BaseModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=30)
    to_status = models.CharField(max_length=30)
    changed_at = models.DateTimeField(auto_now_add=True)

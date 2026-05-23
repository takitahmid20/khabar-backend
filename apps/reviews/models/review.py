from django.db import models

from core.models import BaseModel


class Review(BaseModel):
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reviews")
    order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField()

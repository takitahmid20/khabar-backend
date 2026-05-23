from django.db import models

from core.models import BaseModel


class ProductionLog(BaseModel):
    """Tracks production status for a cook's dish on a specific day."""
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE, related_name="production_logs")
    dish = models.ForeignKey("menu.Dish", on_delete=models.CASCADE, null=True, blank=True)
    dish_key = models.CharField(max_length=200, help_text="dishId::mealSlot composite key")
    date = models.DateField()
    production_status = models.CharField(max_length=30, default="pending")
    is_locked = models.BooleanField(default=False)

    class Meta:
        unique_together = [("cook", "dish_key", "date")]

    def __str__(self):
        return f"{self.dish_key} on {self.date} — {self.production_status}"

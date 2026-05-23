from django.db import models

from core.models import BaseModel


class WeeklyMenu(BaseModel):
    cook = models.ForeignKey("cooks.CookProfile", on_delete=models.CASCADE, related_name="weekly_menus")
    week_start = models.DateField()
    is_active = models.BooleanField(default=True)

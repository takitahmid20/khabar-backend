from django.db import models

from core.models import BaseModel


class Address(BaseModel):
    customer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=50, help_text="e.g. Home, Office")
    division = models.CharField(max_length=50, default="Dhaka")
    district = models.CharField(max_length=50, default="Dhaka")
    sub_district = models.CharField(max_length=100, default="", help_text="e.g. Uttara, Banani, Gulshan")
    line1 = models.CharField(max_length=255, help_text="Exact address / house / road")
    line2 = models.CharField(max_length=255, null=True, blank=True)
    coordinates = models.JSONField(null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.label} - {self.sub_district}, {self.district}"

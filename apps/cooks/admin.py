from django.contrib import admin

from apps.cooks.models import CookProfile, CookVerification


@admin.register(CookProfile)
class CookProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "area_label", "holiday_mode_enabled", "is_verified")


@admin.register(CookVerification)
class CookVerificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")

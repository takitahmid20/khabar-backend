from django.contrib import admin

from apps.locations.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "label", "is_default")

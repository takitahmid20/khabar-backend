from django.contrib import admin

from apps.subscriptions.models import DeliveryInstance, Subscription


class DeliveryInline(admin.TabularInline):
    model = DeliveryInstance
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "cook", "status")
    inlines = [DeliveryInline]

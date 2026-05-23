from rest_framework import serializers

from apps.subscriptions.models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    cook_name = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            "id",
            "cook_id",
            "cook_name",
            "plan_name",
            "meal_slot",
            "portions_per_day",
            "unit_price",
            "monthly_total",
            "status",
            "paused_until",
            "paused_portions",
            "start_date",
            "end_date",
        ]

    def get_cook_name(self, obj):
        if obj.cook and obj.cook.user:
            return obj.cook.user.display_name or "Cook"
        return "Cook"

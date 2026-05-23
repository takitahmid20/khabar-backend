from rest_framework import serializers

from apps.cooks.models import CookProfile


class CookProfileSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="user.display_name", read_only=True)
    mobile = serializers.CharField(source="user.mobile", read_only=True)
    avatar_url = serializers.URLField(source="user.avatar_url", read_only=True)
    verification_status = serializers.CharField(source="user.verification_status", read_only=True)

    class Meta:
        model = CookProfile
        fields = [
            "id",
            "display_name",
            "mobile",
            "avatar_url",
            "verification_status",
            "bio",
            "cuisine_types",
            "specialties",
            "capacity_per_day",
            "rating",
            "review_count",
            "total_orders_count",
            "area_label",
            "radius_km",
            "coordinates",
            "holiday_mode_enabled",
            "payout_method",
            "payout_number",
            "payout_account_name",
            "is_verified",
            "available_balance",
        ]
        read_only_fields = [
            "display_name",
            "mobile",
            "avatar_url",
            "verification_status",
            "rating",
            "review_count",
            "total_orders_count",
            "is_verified",
            "available_balance",
        ]

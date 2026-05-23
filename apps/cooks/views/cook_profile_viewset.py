from rest_framework import permissions, viewsets

from apps.common.models.asset import Asset
from apps.cooks.serializers.cook_profile_serializer import CookProfileSerializer
from apps.cooks.selectors.cook_selector import get_cook_profile
from core.utils import success_response


class CookProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        profile = get_cook_profile(request.user.id)
        serializer = CookProfileSerializer(profile)
        data = serializer.data

        # Live order counts from actual orders table (not stale denormalized field)
        from apps.orders.models import Order
        from shared.enums.core import OrderStatus
        cook_orders = Order.objects.filter(cook=profile)
        data["total_orders_count"] = cook_orders.count()
        data["delivered_orders_count"] = cook_orders.filter(status=OrderStatus.DELIVERED).count()
        data["confirmed_orders_count"] = cook_orders.filter(status=OrderStatus.CONFIRMED).count()

        # Include uploaded document status
        user_assets = Asset.objects.filter(user=request.user).values_list("purpose", flat=True)
        data["has_nid_uploaded"] = "nid_front" in user_assets
        data["has_kitchen_photo_uploaded"] = "kitchen_photo" in user_assets

        return success_response(data)

    def partial_update(self, request):
        profile = get_cook_profile(request.user.id)
        serializer = CookProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data, message="Profile updated")

    def holiday_mode(self, request):
        profile = get_cook_profile(request.user.id)
        profile.holiday_mode_enabled = request.data.get("enabled", False)
        profile.save(update_fields=["holiday_mode_enabled", "updated_at"])
        return success_response({"holidayModeEnabled": profile.holiday_mode_enabled})

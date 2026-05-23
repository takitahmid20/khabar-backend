from rest_framework import permissions, viewsets

from apps.cooks.models import CookProfile
from apps.cooks.serializers.cook_profile_serializer import CookProfileSerializer
from apps.orders.selectors.demand_selector import get_cook_demand
from apps.orders.services.demand_service import DemandService
from core.utils import success_response
from core.permissions import IsCook


class CookDiscoveryViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cooks = CookProfile.objects.select_related("user").filter(
            holiday_mode_enabled=False
        ).order_by("-rating")
        serializer = CookProfileSerializer(cooks, many=True)
        return success_response({"cooks": serializer.data})

    def nearby(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius = int(request.query_params.get("radiusKm", 5))
        cooks = CookProfile.objects.select_related("user").filter(
            holiday_mode_enabled=False, is_verified=True
        ).order_by("-rating")[:20]
        serializer = CookProfileSerializer(cooks, many=True)
        return success_response({"cooks": serializer.data})

    def trending(self, request):
        cooks = CookProfile.objects.select_related("user").filter(
            holiday_mode_enabled=False
        ).order_by("-rating", "-total_orders_count")[:10]
        serializer = CookProfileSerializer(cooks, many=True)
        return success_response({"cooks": serializer.data})

    def search(self, request):
        q = request.query_params.get("q", "")
        cooks = CookProfile.objects.select_related("user").filter(
            holiday_mode_enabled=False,
            user__display_name__icontains=q,
        )[:20]
        serializer = CookProfileSerializer(cooks, many=True)
        return success_response({"cooks": serializer.data})

    def retrieve(self, request, pk=None):
        cook = CookProfile.objects.select_related("user").filter(id=pk).first()
        serializer = CookProfileSerializer(cook)
        return success_response(serializer.data)

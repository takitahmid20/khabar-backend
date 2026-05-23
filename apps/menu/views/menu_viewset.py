from rest_framework import permissions, viewsets

from apps.cooks.models import CookProfile
from apps.menu.serializers.dish_serializer import DishSerializer
from apps.menu.services.dish_service import DishService
from apps.menu.services.menu_builder_service import MenuBuilderService
from core.utils import success_response


class MenuViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "public_menu":
            return [permissions.AllowAny()]
        return [permission() for permission in self.permission_classes]

    def list(self, request):
        cook_profile = CookProfile.objects.filter(user=request.user).first()
        weekly_menu = MenuBuilderService.get_weekly_menu(str(cook_profile.id))
        data = {day: DishSerializer(items, many=True).data for day, items in weekly_menu.items()}
        return success_response({"cookId": str(cook_profile.user_id), "menu": data})

    def create(self, request):
        cook_profile = CookProfile.objects.filter(user=request.user).first()
        serializer = DishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dish = DishService.create_dish(cook_profile, serializer.validated_data)
        return success_response(DishSerializer(dish).data, message="Dish created")

    def partial_update(self, request, pk=None):
        cook_profile = CookProfile.objects.filter(user=request.user).first()
        if not cook_profile:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Cook profile not found.", status_code=404)
        dish = cook_profile.dishes.filter(id=pk).first()
        if not dish:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Dish not found.", status_code=404)
        serializer = DishSerializer(dish, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        dish = DishService.update_dish(dish, serializer.validated_data)
        return success_response(DishSerializer(dish).data, message="Dish updated")

    def destroy(self, request, pk=None):
        cook_profile = CookProfile.objects.filter(user=request.user).first()
        if not cook_profile:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Cook profile not found.", status_code=404)
        dish = cook_profile.dishes.filter(id=pk).first()
        if not dish:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Dish not found.", status_code=404)
        DishService.delete_dish(dish)
        return success_response({}, message="Dish deleted")

    def availability(self, request, pk=None):
        cook_profile = CookProfile.objects.filter(user=request.user).first()
        if not cook_profile:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Cook profile not found.", status_code=404)
        dish = cook_profile.dishes.filter(id=pk).first()
        if not dish:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Dish not found.", status_code=404)
        available = request.data.get("available", True)
        dish = DishService.toggle_availability(dish, available)
        return success_response({"id": str(dish.id), "available": dish.available})

    def public_menu(self, request, cook_id=None):
        weekly_menu = MenuBuilderService.get_weekly_menu(str(cook_id))
        data = {day: DishSerializer(items, many=True).data for day, items in weekly_menu.items()}
        return success_response({"cookId": str(cook_id), "menu": data})

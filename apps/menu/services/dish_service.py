from apps.cooks.models import CookProfile
from apps.menu.models import Dish
from core.exceptions import ServiceException


class DishService:
    @staticmethod
    def create_dish(cook_profile: CookProfile, data: dict) -> Dish:
        return Dish.objects.create(cook=cook_profile, **data)

    @staticmethod
    def update_dish(dish: Dish, data: dict) -> Dish:
        for field, value in data.items():
            setattr(dish, field, value)
        dish.save()
        return dish

    @staticmethod
    def toggle_availability(dish: Dish, available: bool) -> Dish:
        dish.available = available
        dish.save(update_fields=["available", "updated_at"])
        return dish

    @staticmethod
    def delete_dish(dish: Dish) -> None:
        dish.delete()

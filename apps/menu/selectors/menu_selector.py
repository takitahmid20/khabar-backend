from apps.menu.models import Dish


def get_cook_menu_queryset(cook_id):
    return Dish.objects.filter(cook_id=cook_id, available=True)

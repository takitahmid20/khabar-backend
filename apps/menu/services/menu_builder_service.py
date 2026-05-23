from collections import defaultdict

from apps.menu.selectors.menu_selector import get_cook_menu_queryset


class MenuBuilderService:
    @staticmethod
    def get_weekly_menu(cook_id: str) -> dict:
        menu = defaultdict(list)
        queryset = get_cook_menu_queryset(cook_id)
        for dish in queryset:
            for day in dish.days:
                menu[day].append(dish)
        return menu

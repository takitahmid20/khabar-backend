from django.contrib import admin

from apps.menu.models import Dish


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cook", "meal_slot", "price", "available")

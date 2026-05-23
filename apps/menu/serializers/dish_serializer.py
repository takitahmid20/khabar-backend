from rest_framework import serializers

from apps.menu.models import Dish


class DishSerializer(serializers.ModelSerializer):
    # camelCase write aliases that map to snake_case model fields
    mealSlot = serializers.CharField(source="meal_slot", required=False)
    cutoffTime = serializers.CharField(source="cutoff_time", required=False, default="10:00")
    imageUrl = serializers.URLField(source="image_url", required=False, allow_null=True, allow_blank=True)
    addOnsLabel = serializers.CharField(source="add_ons_label", required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Dish
        fields = [
            "id",
            "cook",
            "name",
            "description",
            "category",
            "mealSlot",
            "meal_slot",
            "days",
            "price",
            "capacity",
            "cutoffTime",
            "cutoff_time",
            "imageUrl",
            "image_url",
            "addOnsLabel",
            "add_ons_label",
            "available",
            "is_popular",
        ]
        read_only_fields = ["cook"]
        extra_kwargs = {
            # snake_case fields are read-only (output only)
            "meal_slot": {"read_only": True},
            "cutoff_time": {"read_only": True},
            "image_url": {"read_only": True},
            "add_ons_label": {"read_only": True},
            # Make description optional
            "description": {"required": False, "allow_blank": True, "default": ""},
            "capacity": {"required": False, "default": 0},
            "days": {"required": False, "default": []},
        }

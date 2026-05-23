from rest_framework import serializers

from apps.orders.models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    dishId = serializers.UUIDField(source="dish", write_only=True)
    cookId = serializers.UUIDField(source="cook", write_only=True)
    mealSlot = serializers.CharField(source="meal_slot")
    dayLabel = serializers.CharField(source="day_label")
    planType = serializers.CharField(source="plan_type")
    unitPrice = serializers.DecimalField(source="unit_price", max_digits=10, decimal_places=2)
    monthMultiplier = serializers.IntegerField(source="month_multiplier")
    dishName = serializers.CharField(source="dish_name")
    cookName = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id", "cookId", "cookName", "dishId", "dishName",
            "mealSlot", "dayLabel", "unitPrice", "quantity",
            "monthMultiplier", "planType",
        ]

    def get_cookName(self, obj):
        return obj.cook.user.display_name if obj.cook.user else ""


class CheckoutSummarySerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.DictField(), default=list)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    promoCode = serializers.CharField(allow_blank=True, default="")
    promoDiscount = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    deliveryFee = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    platformFee = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(default="BDT")

from rest_framework import serializers

from apps.orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "dish_name",
            "meal_slot",
            "day_label",
            "quantity",
            "unit_price",
            "month_multiplier",
            "line_total",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    cook_name = serializers.SerializerMethodField()
    delivery_address_label = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "cook_id",
            "cook_name",
            "plan_type",
            "delivery_address_label",
            "subtotal",
            "promo_discount",
            "total_amount",
            "status",
            "payment_status",
            "payment_transaction_id",
            "start_date",
            "end_date",
            "placed_at",
            "items",
        ]

    def get_cook_name(self, obj):
        if obj.cook and obj.cook.user:
            return obj.cook.user.display_name or "Cook"
        return "Cook"

    def get_delivery_address_label(self, obj):
        if obj.delivery_address:
            return f"{obj.delivery_address.label} - {obj.delivery_address.line1}"
        return ""

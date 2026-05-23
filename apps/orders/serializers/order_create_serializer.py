from rest_framework import serializers

from shared.enums.core import PaymentMethod, PlanType


class OrderItemInputSerializer(serializers.Serializer):
    dishId = serializers.UUIDField()
    mealSlot = serializers.CharField(max_length=20)
    dayLabel = serializers.CharField(max_length=20)
    planType = serializers.ChoiceField(choices=PlanType.choices)
    quantity = serializers.IntegerField(min_value=1)
    unitPrice = serializers.DecimalField(max_digits=10, decimal_places=2)
    monthMultiplier = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    cookId = serializers.UUIDField()
    items = OrderItemInputSerializer(many=True)
    deliveryAddressId = serializers.UUIDField()
    paymentMethod = serializers.ChoiceField(choices=PaymentMethod.choices, required=False, default="bkash")
    promoCode = serializers.CharField(max_length=30, required=False, allow_blank=True)
    totalAmount = serializers.DecimalField(max_digits=12, decimal_places=2)

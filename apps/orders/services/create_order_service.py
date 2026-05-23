from django.db import transaction

from apps.cooks.models import CookProfile
from apps.menu.models import Dish
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.orders.services.price_calculation_service import PriceCalculationService
from apps.subscriptions.services.subscription_service import SubscriptionService
from apps.locations.models import Address
from core.exceptions import ServiceException
from shared.enums.core import OrderStatus, PaymentStatus, PlanType


class CreateOrderService:
    @staticmethod
    @transaction.atomic
    def create(customer, data: dict) -> Order:
        cook = CookProfile.objects.filter(id=data["cookId"]).first()
        if not cook:
            raise ServiceException(code="COOK_NOT_FOUND", message="Cook not found")

        address = Address.objects.filter(id=data["deliveryAddressId"], customer=customer).first()
        if not address:
            raise ServiceException(code="ADDRESS_NOT_FOUND", message="Delivery address not found")

        pricing = PriceCalculationService.calculate(data["items"])
        subtotal = pricing["subtotal"]
        promo_discount = 0
        total_amount = subtotal - promo_discount

        order = Order.objects.create(
            customer=customer,
            cook=cook,
            plan_type=data["items"][0]["planType"],
            delivery_address=address,
            payment_method=data["paymentMethod"],
            promo_code=data.get("promoCode"),
            subtotal=subtotal,
            promo_discount=promo_discount,
            total_amount=total_amount,
            status=OrderStatus.PENDING_PAYMENT,
            payment_status=PaymentStatus.PENDING,
        )

        for item in pricing["items"]:
            dish = Dish.objects.filter(id=item["dishId"], cook=cook).first()
            if not dish or not dish.available:
                raise ServiceException(code="DISH_NOT_AVAILABLE", message="Dish not available")
            OrderItem.objects.create(
                order=order,
                dish=dish,
                dish_name=dish.name,
                meal_slot=item["mealSlot"],
                day_label=item["dayLabel"],
                quantity=item["quantity"],
                unit_price=item["unitPrice"],
                month_multiplier=item["monthMultiplier"],
                line_total=item["lineTotal"],
            )

        OrderStatusHistory.objects.create(
            order=order,
            from_status=OrderStatus.PENDING_PAYMENT,
            to_status=OrderStatus.PENDING_PAYMENT,
        )

        if order.plan_type == PlanType.MONTHLY:
            SubscriptionService.create_from_order(order)

        return order

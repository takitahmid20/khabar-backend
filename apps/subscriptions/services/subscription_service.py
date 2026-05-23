from datetime import date

from django.db import transaction

from apps.orders.models import Order
from apps.subscriptions.models import Subscription
from apps.subscriptions.services.delivery_generator_service import DeliveryGeneratorService
from shared.enums.core import PlanType, SubscriptionStatus


class SubscriptionService:
    @staticmethod
    @transaction.atomic
    def create_from_order(order: Order) -> list[Subscription]:
        if order.plan_type != PlanType.MONTHLY:
            return []
        start_date = order.start_date or date.today().replace(day=1)
        end_date = order.end_date or date.today().replace(day=28)

        subscriptions = []
        for item in order.items.all():
            subscription = Subscription.objects.create(
                order=order,
                customer=order.customer,
                cook=order.cook,
                dish=item.dish,
                plan_name=item.dish_name,
                meal_slot=item.meal_slot,
                portions_per_day=item.quantity,
                unit_price=item.unit_price,
                monthly_total=item.line_total,
                status=SubscriptionStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
            )
            DeliveryGeneratorService.generate(subscription, item.day_label, item.quantity)
            subscriptions.append(subscription)
        return subscriptions

    @staticmethod
    def cancel(subscription):
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.save(update_fields=["status", "updated_at"])
        return subscription

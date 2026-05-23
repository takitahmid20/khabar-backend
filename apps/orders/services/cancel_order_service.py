from django.db import transaction

from apps.orders.models import OrderStatusHistory
from core.exceptions import ServiceException
from shared.enums.core import OrderStatus, PaymentStatus


class CancelOrderService:
    @staticmethod
    @transaction.atomic
    def cancel(order):
        if order.status not in [OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED]:
            raise ServiceException(code="ORDER_NOT_CANCELLABLE", message="Order not cancellable")
        order.status = OrderStatus.CANCELLED
        order.payment_status = PaymentStatus.FAILED
        order.save(update_fields=["status", "payment_status", "updated_at"])
        OrderStatusHistory.objects.create(
            order=order,
            from_status=OrderStatus.CONFIRMED,
            to_status=OrderStatus.CANCELLED,
        )
        return order

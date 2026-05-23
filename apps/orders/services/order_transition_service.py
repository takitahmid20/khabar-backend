from django.db import transaction

from apps.orders.models import OrderStatusHistory
from core.exceptions import ServiceException
from shared.enums.core import OrderStatus


class OrderTransitionService:
    ALLOWED = {
        OrderStatus.PENDING_PAYMENT: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
        OrderStatus.PREPARING: [OrderStatus.PACKED],
        OrderStatus.PACKED: [OrderStatus.OUT_FOR_DELIVERY],
        OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED],
    }

    @staticmethod
    @transaction.atomic
    def transition(order, to_status: str):
        allowed = OrderTransitionService.ALLOWED.get(order.status, [])
        if to_status not in allowed:
            raise ServiceException(code="INVALID_STATUS_TRANSITION", message="Invalid status transition")
        from_status = order.status
        order.status = to_status
        order.save(update_fields=["status", "updated_at"])
        OrderStatusHistory.objects.create(order=order, from_status=from_status, to_status=to_status)
        return order

from django.db import transaction

from apps.orders.models import Order
from apps.orders.services.order_transition_service import OrderTransitionService
from apps.payments.models import Payment
from core.exceptions import ServiceException
from shared.enums.core import OrderStatus, PaymentStatus


class PaymentService:
    @staticmethod
    @transaction.atomic
    def confirm_payment(order: Order, transaction_id: str) -> Payment:
        payment = Payment.objects.create(
            order=order,
            method=order.payment_method,
            status=PaymentStatus.PAID,
            amount=order.total_amount,
            transaction_id=transaction_id,
        )
        order.payment_status = PaymentStatus.PAID
        order.save(update_fields=["payment_status", "updated_at"])
        OrderTransitionService.transition(order, OrderStatus.CONFIRMED)
        return payment

    @staticmethod
    @transaction.atomic
    def fail_payment(order: Order, transaction_id: str) -> Payment:
        payment = Payment.objects.create(
            order=order,
            method=order.payment_method,
            status=PaymentStatus.FAILED,
            amount=order.total_amount,
            transaction_id=transaction_id,
        )
        order.payment_status = PaymentStatus.FAILED
        order.status = OrderStatus.CANCELLED
        order.save(update_fields=["payment_status", "status", "updated_at"])
        return payment

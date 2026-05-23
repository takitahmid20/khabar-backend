from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.services.payment_service import PaymentService
from core.exceptions import ServiceException


class WebhookService:
    @staticmethod
    def handle_payment_webhook(order_id: str, status: str, transaction_id: str):
        if Payment.objects.filter(transaction_id=transaction_id).exists():
            return
        order = Order.objects.filter(id=order_id).first()
        if not order:
            raise ServiceException(code="ORDER_NOT_FOUND", message="Order not found")
        if status == "success":
            PaymentService.confirm_payment(order, transaction_id)
        else:
            PaymentService.fail_payment(order, transaction_id)

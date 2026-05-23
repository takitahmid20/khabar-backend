from rest_framework import permissions, viewsets

from apps.orders.models import Order
from apps.payments.services.aamarpay_service import AamarpayService
from core.exceptions import ServiceException
from core.utils import success_response


class PaymentInitiateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def initiate(self, request):
        """Initiate payment for an order via aamarpay."""
        order_id = request.data.get("orderId")
        if not order_id:
            raise ServiceException(code="VALIDATION_ERROR", message="Order ID is required.")

        order = Order.objects.filter(id=order_id, customer=request.user).first()
        if not order:
            raise ServiceException(code="NOT_FOUND", message="Order not found.", status_code=404)

        # Build callback URLs (these would be your server endpoints in production)
        base_url = request.build_absolute_uri("/")[:-1]
        success_url = f"{base_url}/api/v1/payments/callback/success?order_id={order_id}"
        fail_url = f"{base_url}/api/v1/payments/callback/fail?order_id={order_id}"
        cancel_url = f"{base_url}/api/v1/payments/callback/cancel?order_id={order_id}"

        result = AamarpayService.initiate_payment(
            order_id=str(order.id),
            amount=float(order.total_amount),
            customer_name=request.user.display_name or "Customer",
            customer_email=request.user.email or "customer@khabar.app",
            customer_phone=request.user.mobile or "01700000000",
            success_url=success_url,
            fail_url=fail_url,
            cancel_url=cancel_url,
        )

        if result["success"]:
            # Store transaction ID on the order
            order.payment_transaction_id = result["transactionId"]
            order.save(update_fields=["payment_transaction_id", "updated_at"])

            return success_response({
                "paymentUrl": result["paymentUrl"],
                "transactionId": result["transactionId"],
                "orderId": str(order.id),
            })
        else:
            raise ServiceException(
                code="PAYMENT_INIT_FAILED",
                message=f"Payment initiation failed: {result.get('error', 'Unknown error')}",
            )

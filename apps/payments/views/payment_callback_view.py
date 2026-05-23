from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.views import APIView

from apps.orders.models import Order
from shared.enums.core import OrderStatus, PaymentStatus


class PaymentCallbackView(APIView):
    """
    Handles aamarpay payment callbacks (success/fail/cancel).
    These are server-to-server callbacks from aamarpay.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # aamarpay sends payment result as POST data
        pay_status = request.data.get("pay_status", "")
        order_id = request.query_params.get("order_id") or request.data.get("opt_a", "")
        tran_id = request.data.get("mer_txnid", "")

        if not order_id:
            return HttpResponse("Missing order_id", status=400)

        order = Order.objects.filter(id=order_id).first()
        if not order:
            return HttpResponse("Order not found", status=404)

        if pay_status == "Successful":
            order.payment_status = PaymentStatus.PAID
            order.status = OrderStatus.CONFIRMED
            order.payment_transaction_id = tran_id
            order.save(update_fields=["payment_status", "status", "payment_transaction_id", "updated_at"])
            return HttpResponse("Payment successful", status=200)
        elif pay_status == "Failed":
            order.payment_status = PaymentStatus.FAILED
            order.save(update_fields=["payment_status", "updated_at"])
            return HttpResponse("Payment failed", status=200)
        else:
            # Cancelled or unknown
            return HttpResponse("Payment cancelled", status=200)

    def get(self, request):
        # Some callbacks come as GET
        return self.post(request)

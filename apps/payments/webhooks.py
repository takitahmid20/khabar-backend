from rest_framework import permissions, status
from rest_framework.views import APIView

from apps.payments.serializers.webhook_serializer import PaymentWebhookSerializer
from apps.payments.services.webhook_service import WebhookService
from core.utils import success_response


class PaymentWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PaymentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        WebhookService.handle_payment_webhook(
            serializer.validated_data["orderId"],
            serializer.validated_data["status"],
            serializer.validated_data["transactionId"],
        )
        return success_response({}, status_code=status.HTTP_200_OK)

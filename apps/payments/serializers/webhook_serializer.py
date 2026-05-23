from rest_framework import serializers


class PaymentWebhookSerializer(serializers.Serializer):
    orderId = serializers.UUIDField()
    status = serializers.CharField(max_length=20)
    transactionId = serializers.CharField(max_length=120)

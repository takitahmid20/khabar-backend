from rest_framework import serializers

from apps.payments.models import Withdrawal


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ["id", "amount", "payout_method", "payout_number", "status", "processed_at"]

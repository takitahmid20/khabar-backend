from rest_framework import permissions, viewsets

from apps.payments.serializers.withdrawal_serializer import WithdrawalSerializer
from apps.payments.services.earnings_service import EarningsService
from apps.payments.services.withdrawal_service import WithdrawalService
from core.utils import success_response
from core.permissions import IsCook


class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def withdraw(self, request):
        cook_profile = request.user.cook_profile
        amount = request.data.get("amount")
        payout_method = request.data.get("payoutMethod")
        payout_number = request.data.get("payoutNumber")
        withdrawal = WithdrawalService.create_withdrawal(cook_profile, amount, payout_method, payout_number)
        return success_response(WithdrawalSerializer(withdrawal).data, message="Withdrawal initiated")

    def earnings_summary(self, request):
        cook_profile = request.user.cook_profile
        summary = EarningsService.get_summary(cook_profile)
        return success_response(summary)

    def earnings_trend(self, request):
        cook_profile = request.user.cook_profile
        range_type = request.query_params.get("range", "week")
        trend = EarningsService.get_trend(cook_profile, range_type)
        return success_response(trend)

    def earnings_transactions(self, request):
        cook_profile = request.user.cook_profile
        txns = list(EarningsService.get_transactions(cook_profile))
        return success_response({"transactions": txns})

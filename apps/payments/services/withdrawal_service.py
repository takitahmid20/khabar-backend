from django.db import transaction

from apps.payments.models import Withdrawal
from core.exceptions import ServiceException
from shared.enums.core import WithdrawalStatus


class WithdrawalService:
    @staticmethod
    @transaction.atomic
    def create_withdrawal(cook, amount, payout_method, payout_number) -> Withdrawal:
        if amount > cook.available_balance:
            raise ServiceException(code="INSUFFICIENT_BALANCE", message="Insufficient balance")
        withdrawal = Withdrawal.objects.create(
            cook=cook,
            amount=amount,
            payout_method=payout_method,
            payout_number=payout_number,
            status=WithdrawalStatus.PROCESSING,
        )
        cook.available_balance = cook.available_balance - amount
        cook.save(update_fields=["available_balance", "updated_at"])
        return withdrawal

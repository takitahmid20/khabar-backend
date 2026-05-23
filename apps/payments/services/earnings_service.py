from collections import defaultdict
from datetime import datetime

from django.db.models import Sum, Q

from apps.cooks.models import CookProfile
from apps.orders.models import Order, OrderItem
from shared.enums.core import OrderStatus


class EarningsService:
    @staticmethod
    def get_summary(cook_profile: CookProfile) -> dict:
        delivered_orders = Order.objects.filter(
            cook=cook_profile, status=OrderStatus.DELIVERED
        )
        gross = (
            delivered_orders.aggregate(total=Sum("total_amount"))["total"] or 0
        )
        fee_rate = 0.10
        platform_fee = gross * fee_rate
        net = gross - platform_fee
        withdrawn = (
            cook_profile.withdrawals.filter(status="completed").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )
        available = net - withdrawn

        this_month = datetime.now().replace(day=1)
        month_earnings = (
            delivered_orders.filter(placed_at__gte=this_month).aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0
        )

        pending = (
            cook_profile.withdrawals.filter(status="processing").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        return {
            "availableBalance": float(available),
            "totalEarnings": float(gross),
            "thisMonthEarnings": float(month_earnings),
            "platformFeeRate": fee_rate,
            "pendingWithdrawal": float(pending),
        }

    @staticmethod
    def get_trend(cook_profile: CookProfile, range_type: str = "week") -> dict:
        labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        values = [0] * 7
        return {"range": range_type, "labels": labels, "values": values}

    @staticmethod
    def get_transactions(cook_profile: CookProfile):
        return (
            Order.objects.filter(cook=cook_profile)
            .order_by("-placed_at")
            .values("id", "total_amount", "status", "placed_at")[:50]
        )

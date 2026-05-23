from datetime import timedelta

from django.utils import timezone

from core.exceptions import ServiceException
from shared.enums.core import SubscriptionStatus

DURATION_MAP = {
    "1w": 7,
    "2w": 14,
    "1m": 30,
    "manual": None,
}


class PauseService:
    @staticmethod
    def pause(subscription, duration: str, quantity: int):
        if subscription.status != SubscriptionStatus.ACTIVE:
            raise ServiceException(code="SUBSCRIPTION_NOT_ACTIVE", message="Subscription not active")
        subscription.status = SubscriptionStatus.PAUSED
        subscription.paused_portions = quantity
        if DURATION_MAP[duration]:
            subscription.paused_until = timezone.now() + timedelta(days=DURATION_MAP[duration])
        subscription.save(update_fields=["status", "paused_portions", "paused_until", "updated_at"])
        return subscription

    @staticmethod
    def resume(subscription):
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.paused_until = None
        subscription.paused_portions = 0
        subscription.save(update_fields=["status", "paused_until", "paused_portions", "updated_at"])
        return subscription

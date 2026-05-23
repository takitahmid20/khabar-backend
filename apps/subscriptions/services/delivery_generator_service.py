import calendar
from datetime import date, timedelta

from apps.subscriptions.models import DeliveryInstance
from shared.enums.core import DeliveryStatus

DAY_LABEL_TO_WEEKDAY = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}


class DeliveryGeneratorService:
    @staticmethod
    def generate(subscription, day_label: str, quantity: int):
        start = subscription.start_date
        end = subscription.end_date
        target_weekday = DAY_LABEL_TO_WEEKDAY[day_label.lower()]

        current = start
        while current <= end:
            if current.weekday() == target_weekday:
                DeliveryInstance.objects.create(
                    subscription=subscription,
                    customer=subscription.customer,
                    cook=subscription.cook,
                    date=current,
                    status=DeliveryStatus.SCHEDULED,
                    quantity_ordered=quantity,
                )
            current += timedelta(days=1)

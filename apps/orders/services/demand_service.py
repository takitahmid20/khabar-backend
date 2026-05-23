from django.db import transaction

from apps.orders.models import DemandItem
from core.exceptions import ServiceException
from shared.enums.core import DemandStatus

VALID_TRANSITIONS = {
    DemandStatus.PENDING: [DemandStatus.PREPARING],
    DemandStatus.PREPARING: [DemandStatus.PACKED],
    DemandStatus.PACKED: [DemandStatus.OUT_FOR_DELIVERY],
    DemandStatus.OUT_FOR_DELIVERY: [DemandStatus.DELIVERED],
}


class DemandService:
    @staticmethod
    @transaction.atomic
    def lock_item(item_id, user):
        item = DemandItem.objects.filter(id=item_id, cook__user=user).first()
        if not item:
            raise ServiceException(code="DEMAND_ITEM_NOT_FOUND", message="Demand item not found")
        if item.is_locked:
            raise ServiceException(code="PLAN_ALREADY_LOCKED", message="Plan already locked")
        item.is_locked = True
        item.save(update_fields=["is_locked", "updated_at"])
        return item

    @staticmethod
    @transaction.atomic
    def advance_status(item_id, user, status):
        item = DemandItem.objects.filter(id=item_id, cook__user=user).first()
        if not item:
            raise ServiceException(code="DEMAND_ITEM_NOT_FOUND", message="Demand item not found")
        allowed = VALID_TRANSITIONS.get(item.production_status, [])
        if status not in allowed:
            raise ServiceException(code="INVALID_STATUS_TRANSITION", message="Invalid status transition")
        item.production_status = status
        item.save(update_fields=["production_status", "updated_at"])
        return item

from collections import defaultdict
from datetime import date as date_type

from django.db.models import Q
from rest_framework import permissions, viewsets

from apps.cooks.models import CookProfile
from apps.orders.models import Order, OrderItem
from apps.orders.services.demand_service import DemandService
from core.utils import success_response
from shared.enums.core import OrderStatus, DayKey


# Map full day names to short DayKey values
DAY_NAME_TO_KEY = {
    "Monday": "mon",
    "Tuesday": "tue",
    "Wednesday": "wed",
    "Thursday": "thu",
    "Friday": "fri",
    "Saturday": "sat",
    "Sunday": "sun",
}

WEEKDAY_TO_NAME = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


class DemandViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        today = date_type.today()
        today_name = WEEKDAY_TO_NAME[today.weekday()]
        today_key = DAY_NAME_TO_KEY[today_name]

        cook_profile = CookProfile.objects.filter(user=request.user).first()
        if not cook_profile:
            return success_response({"date": str(today), "demandItems": []})

        # Get all confirmed orders for this cook
        confirmed_statuses = [
            OrderStatus.CONFIRMED,
            OrderStatus.PREPARING,
            OrderStatus.PACKED,
            OrderStatus.OUT_FOR_DELIVERY,
        ]

        # Today's order items for this cook:
        # - Today's plan means day_label matches today (for monthly), or placed today (for single-day)
        order_items = (
            OrderItem.objects.filter(
                order__cook=cook_profile,
                order__status__in=confirmed_statuses,
            )
            .filter(
                # Monthly subscriptions: day_label matches today's name
                Q(order__plan_type="monthly", day_label__iexact=today_name)
                |
                # Single-day orders: placed today
                Q(order__plan_type="today", order__placed_at__date=today)
            )
            .select_related("order", "order__customer", "dish")
        )

        # Group by dish_name + meal_slot
        groups = defaultdict(lambda: {
            "dishId": None,
            "dishName": "",
            "mealSlot": "",
            "cutoffTime": "10:00",
            "capacity": 0,
            "totalQuantity": 0,
            "subscriptionQty": 0,
            "oneOffQty": 0,
            "customers": [],
        })

        for item in order_items:
            key = f"{item.dish_id}::{item.meal_slot}"
            g = groups[key]
            g["dishId"] = str(item.dish_id) if item.dish else None
            g["dishName"] = item.dish_name
            g["mealSlot"] = item.meal_slot
            if item.dish and item.dish.cutoff_time:
                g["cutoffTime"] = item.dish.cutoff_time.strftime("%H:%M")
            if item.dish:
                g["capacity"] = item.dish.capacity or 0

            g["totalQuantity"] += item.quantity
            if item.order.plan_type == "monthly":
                g["subscriptionQty"] += item.quantity
            else:
                g["oneOffQty"] += item.quantity

            customer = item.order.customer
            g["customers"].append({
                "orderId": str(item.order.id),
                "_orderId": item.order.id,  # raw UUID for delivery lookup
                "customerName": customer.display_name or customer.mobile or "Customer",
                "customerMobile": customer.mobile,
                "quantity": item.quantity,
                "planType": item.order.plan_type,
                "orderStatus": item.order.status,
            })

        # Get production log for today to restore persisted status
        from apps.orders.models import ProductionLog, OrderDelivery
        from django.utils import timezone

        production_logs = {
            log.dish_key: log
            for log in ProductionLog.objects.filter(cook=cook_profile, date=today)
        }

        # Get delivery status per order per dish
        delivery_records = {}
        for od in OrderDelivery.objects.filter(
            order__cook=cook_profile, date=today
        ):
            delivery_records[(od.order_id, od.dish_key)] = od.is_delivered

        demand_items = [
            {
                "id": key,
                "dishId": g["dishId"],
                "dishName": g["dishName"],
                "mealSlot": g["mealSlot"],
                "cutoffLabel": f"Cutoff {g['cutoffTime']}",
                "cutoffTime": g["cutoffTime"],
                "baseline": g["subscriptionQty"],
                "oneOff": g["oneOffQty"],
                "overrides": 0,
                "cancellations": 0,
                "capacity": g["capacity"],
                "isLocked": production_logs.get(key, None) is not None and production_logs[key].is_locked,
                "productionStatus": production_logs[key].production_status if key in production_logs else "pending",
                "totalQuantity": g["totalQuantity"],
                "customers": [
                    {**c, "delivered": delivery_records.get((c["_orderId"], key), False)}
                    for c in g["customers"]
                ],
            }
            for key, g in groups.items()
        ]

        # Sort by meal slot order
        slot_order = {"Breakfast": 0, "Lunch": 1, "Dinner": 2}
        demand_items.sort(key=lambda x: slot_order.get(x["mealSlot"], 99))

        return success_response({
            "date": today_name,
            "demandItems": demand_items,
        })

    def lock(self, request, pk=None):
        from apps.orders.models import ProductionLog
        from datetime import date as date_type
        cook_profile = CookProfile.objects.filter(user=request.user).first()
        if not cook_profile:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Cook profile not found.", status_code=404)
        today = date_type.today()
        log, _ = ProductionLog.objects.get_or_create(
            cook=cook_profile, dish_key=pk, date=today,
            defaults={"production_status": "pending"},
        )
        log.is_locked = True
        log.save(update_fields=["is_locked", "updated_at"])
        return success_response({"dishKey": pk, "isLocked": True}, message="Locked")

    def advance_status(self, request, pk=None):
        from apps.orders.models import ProductionLog
        from datetime import date as date_type
        cook_profile = CookProfile.objects.filter(user=request.user).first()
        if not cook_profile:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Cook profile not found.", status_code=404)
        status = request.data.get("status")
        today = date_type.today()
        log, _ = ProductionLog.objects.get_or_create(
            cook=cook_profile, dish_key=pk, date=today,
            defaults={"production_status": "pending"},
        )
        log.production_status = status
        log.save(update_fields=["production_status", "updated_at"])
        return success_response({"dishKey": pk, "productionStatus": status})

    def mark_delivered(self, request, pk=None):
        """Mark a specific order's delivery for this dish as delivered."""
        from apps.orders.models import OrderDelivery, Order
        from datetime import date as date_type
        from django.utils import timezone

        cook_profile = CookProfile.objects.filter(user=request.user).first()
        order_id = request.data.get("orderId")
        today = date_type.today()

        try:
            order = Order.objects.get(id=order_id, cook=cook_profile)
        except Order.DoesNotExist:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Order not found.", status_code=404)

        od, _ = OrderDelivery.objects.get_or_create(
            order=order, dish_key=pk, date=today,
        )
        od.is_delivered = True
        od.delivered_at = timezone.now()
        od.save(update_fields=["is_delivered", "delivered_at", "updated_at"])
        return success_response({"orderId": order_id, "dishKey": pk, "delivered": True})

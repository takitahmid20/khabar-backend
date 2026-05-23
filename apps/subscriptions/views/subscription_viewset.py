from rest_framework import permissions, viewsets

from apps.subscriptions.serializers.subscription_action_serializer import PauseSubscriptionSerializer, SkipDeliverySerializer
from apps.subscriptions.serializers.subscription_serializer import SubscriptionSerializer
from apps.subscriptions.selectors.subscription_selector import get_subscription, list_subscriptions
from apps.subscriptions.services.pause_service import PauseService
from apps.subscriptions.services.subscription_service import SubscriptionService
from core.utils import success_response
from shared.enums.core import DeliveryStatus
from apps.subscriptions.models import DeliveryInstance


class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        subscriptions = list_subscriptions(request.user.id)
        return success_response({"subscriptions": SubscriptionSerializer(subscriptions, many=True).data})

    def retrieve(self, request, pk=None):
        subscription = get_subscription(pk, request.user.id)
        return success_response(SubscriptionSerializer(subscription).data)

    def pause(self, request, pk=None):
        serializer = PauseSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = get_subscription(pk, request.user.id)
        subscription = PauseService.pause(subscription, serializer.validated_data["duration"], serializer.validated_data["quantity"])
        return success_response(SubscriptionSerializer(subscription).data)

    def resume(self, request, pk=None):
        subscription = get_subscription(pk, request.user.id)
        subscription = PauseService.resume(subscription)
        return success_response(SubscriptionSerializer(subscription).data)

    def cancel(self, request, pk=None):
        subscription = get_subscription(pk, request.user.id)
        subscription = SubscriptionService.cancel(subscription)
        return success_response(SubscriptionSerializer(subscription).data)

    def calendar(self, request, pk=None):
        subscription = get_subscription(pk, request.user.id)
        month = request.query_params.get("month")
        deliveries = subscription.deliveries.all()
        if month:
            deliveries = deliveries.filter(date__startswith=month)
        data = [
            {
                "id": str(delivery.id),
                "date": delivery.date.isoformat(),
                "status": delivery.status,
                "quantityOrdered": delivery.quantity_ordered,
                "quantityDelivered": delivery.quantity_delivered,
                "quantitySkipped": delivery.quantity_skipped,
                "undoableUntil": delivery.undoable_until.isoformat() if delivery.undoable_until else None,
            }
            for delivery in deliveries
        ]
        return success_response({"month": month, "deliveries": data})

    def skip_delivery(self, request, pk=None, delivery_id=None):
        serializer = SkipDeliverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = get_subscription(pk, request.user.id)
        delivery = DeliveryInstance.objects.filter(id=delivery_id, subscription=subscription).first()
        delivery.quantity_skipped = serializer.validated_data["quantity"]
        if delivery.quantity_skipped >= delivery.quantity_ordered:
            delivery.status = DeliveryStatus.SKIPPED
        delivery.save(update_fields=["quantity_skipped", "status", "updated_at"])
        return success_response({"deliveryId": str(delivery.id), "status": delivery.status})

    def resume_delivery(self, request, pk=None, delivery_id=None):
        subscription = get_subscription(pk, request.user.id)
        delivery = DeliveryInstance.objects.filter(id=delivery_id, subscription=subscription).first()
        delivery.quantity_skipped = 0
        delivery.status = DeliveryStatus.SCHEDULED
        delivery.save(update_fields=["quantity_skipped", "status", "updated_at"])
        return success_response({"deliveryId": str(delivery.id), "status": delivery.status})


class CookSubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, pk=None):
        """Get full subscription detail with delivery calendar for cook."""
        from apps.cooks.models import CookProfile
        from apps.subscriptions.models import Subscription
        from core.exceptions import ServiceException

        cook_profile = CookProfile.objects.filter(user=request.user).first()
        if not cook_profile:
            raise ServiceException(code="NOT_FOUND", message="Cook profile not found.", status_code=404)

        try:
            sub = Subscription.objects.select_related("customer", "dish", "order", "order__delivery_address").get(
                id=pk, cook=cook_profile
            )
        except Subscription.DoesNotExist:
            raise ServiceException(code="NOT_FOUND", message="Subscription not found.", status_code=404)

        order_items = list(
            sub.order.items.values("dish_name", "meal_slot", "day_label", "quantity", "unit_price")
        ) if sub.order else []

        deliveries = []
        for delivery in sub.deliveries.order_by("date"):
            deliveries.append({
                "id": str(delivery.id),
                "date": str(delivery.date),
                "status": delivery.status,
                "quantityOrdered": delivery.quantity_ordered,
                "quantityDelivered": delivery.quantity_delivered,
                "quantitySkipped": delivery.quantity_skipped,
                "skippedByCustomer": delivery.quantity_skipped > 0,
                "effectiveQuantity": max(0, delivery.quantity_ordered - delivery.quantity_skipped),
                "undoableUntil": delivery.undoable_until.isoformat() if delivery.undoable_until else None,
            })

        # Delivery address from the linked order
        delivery_address = None
        if sub.order and sub.order.delivery_address:
            addr = sub.order.delivery_address
            delivery_address = {
                "label": addr.label,
                "subDistrict": addr.sub_district,
                "district": addr.district,
                "division": addr.division,
                "line1": addr.line1,
            }

        data = {
            "id": str(sub.id),
            "status": sub.status,
            "customerName": sub.customer.display_name or sub.customer.mobile or "Customer",
            "customerMobile": sub.customer.mobile,
            "customerEmail": sub.customer.email,
            "planName": sub.plan_name,
            "mealSlot": sub.meal_slot,
            "portionsPerDay": sub.portions_per_day,
            "unitPrice": float(sub.unit_price),
            "monthlyTotal": float(sub.monthly_total),
            "startDate": str(sub.start_date),
            "endDate": str(sub.end_date),
            "pausedUntil": sub.paused_until.isoformat() if sub.paused_until else None,
            "pausedPortions": sub.paused_portions,
            "deliveryAddress": delivery_address,
            "orderItems": order_items,
            "deliveries": deliveries,
            "totalDeliveries": len(deliveries),
            "deliveredCount": sum(1 for d in deliveries if d["status"] == "delivered"),
            "skippedCount": sum(1 for d in deliveries if d["skippedByCustomer"]),
            "remainingCount": sum(1 for d in deliveries if d["status"] == "scheduled"),
            "totalSkippedPortions": sum(d["quantitySkipped"] for d in deliveries),
        }
        return success_response(data)

    def list(self, request):
        """List all active subscriptions for the cook with full details."""
        from apps.cooks.models import CookProfile
        from apps.subscriptions.models import Subscription
        from shared.enums.core import SubscriptionStatus

        cook_profile = CookProfile.objects.filter(user=request.user).first()
        if not cook_profile:
            return success_response({"subscriptions": []})

        subscriptions = (
            Subscription.objects.filter(cook=cook_profile)
            .select_related("customer", "dish", "order")
            .order_by("-created_at")
        )

        data = []
        for sub in subscriptions:
            # Get the order items for this subscription's order
            order_items = list(
                sub.order.items.values("dish_name", "meal_slot", "day_label", "quantity", "unit_price")
            ) if sub.order else []

            data.append({
                "id": str(sub.id),
                "status": sub.status,
                "customerName": sub.customer.display_name or sub.customer.mobile or "Customer",
                "customerMobile": sub.customer.mobile,
                "planName": sub.plan_name,
                "mealSlot": sub.meal_slot,
                "portionsPerDay": sub.portions_per_day,
                "unitPrice": float(sub.unit_price),
                "monthlyTotal": float(sub.monthly_total),
                "startDate": str(sub.start_date),
                "endDate": str(sub.end_date),
                "pausedUntil": sub.paused_until.isoformat() if sub.paused_until else None,
                "pausedPortions": sub.paused_portions,
                "orderItems": order_items,
            })

        return success_response({"subscriptions": data})

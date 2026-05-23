from rest_framework import permissions, viewsets

from apps.orders.serializers.order_create_serializer import OrderCreateSerializer
from apps.orders.serializers.order_detail_serializer import OrderDetailSerializer
from apps.orders.selectors.order_selector import get_order_detail, list_customer_orders
from apps.orders.services.cancel_order_service import CancelOrderService
from apps.orders.services.create_order_service import CreateOrderService
from core.utils import success_response


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = CreateOrderService.create(request.user, serializer.validated_data)
        return success_response(OrderDetailSerializer(order).data, message="Order created")

    def list(self, request):
        status_filter = request.query_params.get("status")
        orders = list_customer_orders(request.user.id, status_filter)
        serializer = OrderDetailSerializer(orders, many=True)
        return success_response({"orders": serializer.data})

    def retrieve(self, request, pk=None):
        order = get_order_detail(pk, request.user.id)
        serializer = OrderDetailSerializer(order)
        return success_response(serializer.data)

    def cancel(self, request, pk=None):
        order = get_order_detail(pk, request.user.id)
        order = CancelOrderService.cancel(order)
        return success_response({"id": str(order.id), "status": order.status}, message="Order cancelled")

    def cook_orders(self, request):
        """List all orders for the cook (order history)."""
        from apps.cooks.models import CookProfile
        from shared.enums.core import OrderStatus
        cook_profile = CookProfile.objects.filter(user=request.user).first()
        if not cook_profile:
            return success_response({"orders": []})
        orders = Order.objects.filter(cook=cook_profile).order_by("-placed_at").select_related(
            "customer", "delivery_address"
        ).prefetch_related("items")
        serializer = OrderDetailSerializer(orders, many=True)
        return success_response({"orders": serializer.data})
        order = get_order_detail(pk, request.user.id)
        if not order:
            return success_response({}, message="Order not found")
        from apps.orders.services.cart_service import CartService
        CartService.clear_cart(request.user.id)
        for item in order.items.all():
            CartService.add_item(request.user, {
                "cook": order.cook,
                "dish": item.dish,
                "dish_name": item.dish_name,
                "meal_slot": item.meal_slot,
                "day_label": item.day_label,
                "plan_type": order.plan_type,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "month_multiplier": item.month_multiplier,
            })
        return success_response({"orderId": str(order.id)}, message="Items added to cart")

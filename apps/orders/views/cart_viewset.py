from rest_framework import permissions, viewsets

from apps.orders.selectors.cart_selector import get_cart_items
from apps.orders.serializers.cart_serializer import CartItemSerializer, CheckoutSummarySerializer
from apps.orders.services.cart_service import CartService
from apps.orders.services.checkout_service import CheckoutService
from core.utils import success_response


class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        items = get_cart_items(request.user.id)
        serializer = CartItemSerializer(items, many=True)
        return success_response({"items": serializer.data})

    def add(self, request):
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = CartService.add_item(request.user, serializer.validated_data)
        return success_response(CartItemSerializer(item).data, message="Item added")

    def partial_update(self, request, pk=None):
        item = CartService.update_quantity(request.user.id, pk, request.data.get("quantity", 1))
        return success_response(CartItemSerializer(item).data)

    def destroy(self, request, pk=None):
        CartService.remove_item(request.user.id, pk)
        return success_response({}, message="Item removed")

    def clear(self, request):
        CartService.clear_cart(request.user.id)
        return success_response({}, message="Cart cleared")

    def add_promo(self, request):
        return success_response({"promoCode": request.data.get("promoCode")}, message="Promo applied")

    def remove_promo(self, request):
        return success_response({}, message="Promo removed")

    def summary(self, request):
        items = get_cart_items(request.user.id)
        result = CheckoutService.calculate_summary(items)
        return success_response(CheckoutSummarySerializer(result).data)

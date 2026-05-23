from django.urls import path

from apps.orders.views.cart_viewset import CartViewSet
from apps.orders.views.demand_viewset import DemandViewSet
from apps.orders.views.order_viewset import OrderViewSet

urlpatterns = [
    # Orders
    path("orders", OrderViewSet.as_view({"post": "create"}), name="order-create"),
    path("customer/orders", OrderViewSet.as_view({"get": "list"}), name="customer-orders"),
    path("customer/orders/<uuid:pk>", OrderViewSet.as_view({"get": "retrieve"}), name="customer-order-detail"),
    path("customer/orders/<uuid:pk>/cancel", OrderViewSet.as_view({"post": "cancel"}), name="customer-order-cancel"),
    path("customer/orders/<uuid:pk>/reorder", OrderViewSet.as_view({"post": "reorder"}), name="customer-order-reorder"),
    # Cart
    path("cart", CartViewSet.as_view({"get": "list", "delete": "clear"}), name="cart"),
    path("cart/items", CartViewSet.as_view({"post": "add"}), name="cart-add"),
    path("cart/items/<uuid:pk>", CartViewSet.as_view({"patch": "partial_update", "delete": "destroy"}), name="cart-item"),
    path("cart/promo", CartViewSet.as_view({"post": "add_promo", "delete": "remove_promo"}), name="cart-promo"),
    path("checkout/summary", CartViewSet.as_view({"get": "summary"}), name="checkout-summary"),
    # Cook demand
    path("cook/demand", DemandViewSet.as_view({"get": "list"}), name="cook-demand"),
    path("cook/demand/<str:pk>/lock", DemandViewSet.as_view({"post": "lock"}), name="cook-demand-lock"),
    path("cook/demand/<str:pk>/status", DemandViewSet.as_view({"patch": "advance_status"}), name="cook-demand-status"),
    path("cook/demand/<str:pk>/deliver", DemandViewSet.as_view({"post": "mark_delivered"}), name="cook-demand-deliver"),
    # Cook order history
    path("cook/orders", OrderViewSet.as_view({"get": "cook_orders"}), name="cook-orders"),
]

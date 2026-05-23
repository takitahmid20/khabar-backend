from apps.orders.models import Order


def get_order_detail(order_id, customer_id=None):
    queryset = Order.objects.select_related("cook", "delivery_address").prefetch_related("items")
    if customer_id:
        queryset = queryset.filter(customer_id=customer_id)
    return queryset.filter(id=order_id).first()


def list_customer_orders(customer_id, status=None):
    queryset = Order.objects.select_related("cook").filter(customer_id=customer_id)
    if status:
        queryset = queryset.filter(status=status)
    return queryset.order_by("-placed_at")

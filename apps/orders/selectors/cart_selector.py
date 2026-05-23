from apps.orders.models import CartItem


def get_cart_items(customer_id):
    return CartItem.objects.select_related("cook__user", "dish").filter(customer_id=customer_id)

from django.db import transaction

from apps.orders.models import CartItem
from core.exceptions import ServiceException


class CartService:
    @staticmethod
    @transaction.atomic
    def add_item(customer, data: dict) -> CartItem:
        return CartItem.objects.create(customer=customer, **data)

    @staticmethod
    @transaction.atomic
    def update_quantity(customer_id, item_id, quantity):
        item = CartItem.objects.filter(id=item_id, customer_id=customer_id).first()
        if not item:
            raise ServiceException(code="CART_ITEM_NOT_FOUND", message="Cart item not found")
        item.quantity = quantity
        item.save(update_fields=["quantity", "updated_at"])
        return item

    @staticmethod
    @transaction.atomic
    def remove_item(customer_id, item_id):
        CartItem.objects.filter(id=item_id, customer_id=customer_id).delete()

    @staticmethod
    @transaction.atomic
    def clear_cart(customer_id):
        CartItem.objects.filter(customer_id=customer_id).delete()

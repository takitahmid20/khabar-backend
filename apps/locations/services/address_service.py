from django.db import transaction

from apps.locations.models import Address


class AddressService:
    @staticmethod
    def list_addresses(customer):
        return Address.objects.filter(customer=customer).order_by("-created_at")

    @staticmethod
    @transaction.atomic
    def create_address(customer, data: dict) -> Address:
        is_default = data.get("is_default", False)
        if is_default:
            Address.objects.filter(customer=customer, is_default=True).update(is_default=False)
        address = Address.objects.create(customer=customer, **data)
        if Address.objects.filter(customer=customer).count() == 1:
            address.is_default = True
            address.save(update_fields=["is_default", "updated_at"])
        return address

    @staticmethod
    @transaction.atomic
    def update_address(address: Address, data: dict) -> Address:
        for field, value in data.items():
            setattr(address, field, value)
        address.save()
        return address

    @staticmethod
    @transaction.atomic
    def delete_address(address: Address) -> None:
        address.delete()

    @staticmethod
    @transaction.atomic
    def set_default(address: Address) -> Address:
        Address.objects.filter(customer=address.customer, is_default=True).update(is_default=False)
        address.is_default = True
        address.save(update_fields=["is_default", "updated_at"])
        return address

from apps.locations.models import Address


def get_address(address_id, customer_id):
    return Address.objects.filter(id=address_id, customer_id=customer_id).first()

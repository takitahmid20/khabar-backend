from rest_framework import permissions, viewsets

from apps.locations.selectors.address_selector import get_address
from apps.locations.serializers.address_serializer import AddressSerializer
from apps.locations.services.address_service import AddressService
from core.utils import success_response


class AddressViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        addresses = AddressService.list_addresses(request.user)
        return success_response({"addresses": AddressSerializer(addresses, many=True).data})

    def create(self, request):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = AddressService.create_address(request.user, serializer.validated_data)
        return success_response(AddressSerializer(address).data, message="Address created")

    def partial_update(self, request, pk=None):
        address = get_address(pk, request.user.id)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        address = AddressService.update_address(address, serializer.validated_data)
        return success_response(AddressSerializer(address).data, message="Address updated")

    def destroy(self, request, pk=None):
        address = get_address(pk, request.user.id)
        if not address:
            from core.exceptions import ServiceException
            raise ServiceException(code="NOT_FOUND", message="Address not found.", status_code=404)
        AddressService.delete_address(address)
        return success_response({}, message="Address deleted")

    def set_default(self, request, pk=None):
        address = get_address(pk, request.user.id)
        address = AddressService.set_default(address)
        return success_response(AddressSerializer(address).data)

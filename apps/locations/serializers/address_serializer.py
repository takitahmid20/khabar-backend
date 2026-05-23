from rest_framework import serializers

from apps.locations.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "label",
            "division",
            "district",
            "sub_district",
            "line1",
            "line2",
            "coordinates",
            "is_default",
        ]
        extra_kwargs = {
            "division": {"required": False, "default": "Dhaka"},
            "district": {"required": False, "default": "Dhaka"},
            "line2": {"required": False, "allow_blank": True},
        }

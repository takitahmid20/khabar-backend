from rest_framework import serializers

from apps.auth.models.otp import OTP
from shared.enums.core import UserRole


class OtpVerifySerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=OTP.Method.choices)
    destination = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=6)
    role = serializers.ChoiceField(choices=UserRole.choices)

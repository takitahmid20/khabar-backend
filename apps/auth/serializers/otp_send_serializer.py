import re

from rest_framework import serializers

from apps.auth.models.otp import OTP
from shared.enums.core import UserRole


class OtpSendSerializer(serializers.Serializer):
    method = serializers.ChoiceField(
        choices=OTP.Method.choices,
        error_messages={
            "invalid_choice": "Please select a valid method (mobile or email).",
        },
    )
    destination = serializers.CharField(max_length=255)
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        error_messages={
            "invalid_choice": "Please select a valid role (cook or customer).",
        },
    )

    def validate_destination(self, value):
        method = self.initial_data.get("method")
        if method == "mobile":
            # Expect format like +880XXXXXXXXXX (Bangladesh)
            cleaned = value.strip()
            if not re.match(r"^\+880\d{10}$", cleaned):
                raise serializers.ValidationError(
                    "Please enter a valid Bangladesh mobile number (e.g. +8801XXXXXXXXX)."
                )
            return cleaned
        elif method == "email":
            cleaned = value.strip().lower()
            if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", cleaned):
                raise serializers.ValidationError(
                    "Please enter a valid email address."
                )
            return cleaned
        return value.strip()

from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    has_pin = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "role",
            "display_name",
            "avatar_url",
            "mobile",
            "email",
            "verification_status",
            "onboarding_completed",
            "onboarding_step",
            "has_pin",
            "created_at",
        ]

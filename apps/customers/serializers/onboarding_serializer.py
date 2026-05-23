from rest_framework import serializers


class CustomerOnboardingSerializer(serializers.Serializer):
    displayName = serializers.CharField(max_length=120)
    avatarUrl = serializers.URLField(required=False, allow_null=True)

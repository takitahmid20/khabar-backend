from rest_framework import serializers


class TokenRefreshSerializer(serializers.Serializer):
    refreshToken = serializers.CharField()

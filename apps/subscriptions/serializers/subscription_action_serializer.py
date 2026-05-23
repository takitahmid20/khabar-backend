from rest_framework import serializers


class PauseSubscriptionSerializer(serializers.Serializer):
    duration = serializers.ChoiceField(choices=["1w", "2w", "1m", "manual"])
    quantity = serializers.IntegerField(min_value=1)


class SkipDeliverySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

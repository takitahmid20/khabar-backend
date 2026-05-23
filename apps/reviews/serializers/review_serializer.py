from rest_framework import serializers

from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    cookId = serializers.UUIDField(source="cook", write_only=True, required=False)
    orderId = serializers.UUIDField(source="order", write_only=True, required=False, allow_null=True)

    class Meta:
        model = Review
        fields = ["id", "cook", "cookId", "order", "orderId", "rating", "comment", "created_at"]

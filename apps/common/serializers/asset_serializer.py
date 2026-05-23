from rest_framework import serializers

from apps.common.models.asset import Asset


class AssetUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    purpose = serializers.ChoiceField(
        choices=Asset.Purpose.choices,
        error_messages={
            "invalid_choice": "Invalid purpose. Valid options: avatar, kitchen_photo, nid_front, nid_back, selfie, menu_item, general.",
        },
    )


class AssetResponseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ["id", "url", "purpose", "mime_type", "file_size", "original_filename", "created_at"]

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        elif obj.file:
            return obj.file.url
        return None

from rest_framework import permissions, viewsets
from rest_framework.parsers import MultiPartParser

from apps.common.serializers.asset_serializer import AssetResponseSerializer, AssetUploadSerializer
from apps.common.services.upload_service import UploadService
from core.utils import success_response


class UploadViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def create(self, request):
        serializer = AssetUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        asset = UploadService.upload_file(
            user=request.user,
            file=serializer.validated_data["file"],
            purpose=serializer.validated_data["purpose"],
        )

        response_data = AssetResponseSerializer(asset, context={"request": request}).data
        return success_response(response_data, message="File uploaded successfully")

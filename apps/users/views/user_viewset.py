from rest_framework import permissions, viewsets

from apps.users.serializers.user_serializer import UserSerializer
from apps.users.services.user_service import UserService
from core.utils import success_response


class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        serializer = UserSerializer(request.user)
        return success_response(serializer.data)

    def partial_update(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = UserService.update_profile(request.user, serializer.validated_data)
        return success_response(UserSerializer(user).data, message="Profile updated")

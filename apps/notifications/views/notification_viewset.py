from rest_framework import permissions, viewsets

from apps.notifications.selectors.notification_selector import list_notifications, unread_count
from apps.notifications.serializers.notification_serializer import NotificationSerializer
from core.utils import success_response


class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        notifications = list_notifications(request.user.id)
        return success_response({"notifications": NotificationSerializer(notifications, many=True).data})

    def mark_read(self, request, pk=None):
        notification = request.user.notifications.filter(id=pk).first()
        if notification:
            notification.is_read = True
            notification.save(update_fields=["is_read", "updated_at"])
        return success_response({"id": str(notification.id), "isRead": True})

    def read_all(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return success_response({"success": True})

    def unread_count(self, request):
        count = unread_count(request.user.id)
        return success_response({"count": count})

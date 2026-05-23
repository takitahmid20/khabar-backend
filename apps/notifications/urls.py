from django.urls import path

from apps.notifications.views.notification_viewset import NotificationViewSet

urlpatterns = [
    path("notifications", NotificationViewSet.as_view({"get": "list"}), name="notifications"),
    path("notifications/<uuid:pk>/read", NotificationViewSet.as_view({"patch": "mark_read"}), name="notification-read"),
    path("notifications/read-all", NotificationViewSet.as_view({"patch": "read_all"}), name="notifications-read-all"),
    path("notifications/unread-count", NotificationViewSet.as_view({"get": "unread_count"}), name="notifications-unread-count"),
]

from apps.notifications.models import Notification


def list_notifications(user_id):
    return Notification.objects.filter(user_id=user_id).order_by("-created_at")


def unread_count(user_id):
    return Notification.objects.filter(user_id=user_id, is_read=False).count()

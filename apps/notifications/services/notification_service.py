from apps.notifications.models import Notification


class NotificationService:
    @staticmethod
    def create(user, event_key: str, title: str, body: str, data: dict | None = None) -> Notification:
        return Notification.objects.create(
            user=user,
            event_key=event_key,
            title=title,
            body=body,
            data=data or {},
        )

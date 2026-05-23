from apps.notifications.services.notification_service import NotificationService


class EventDispatcher:
    @staticmethod
    def dispatch(user, event_key: str, title: str, body: str, data: dict | None = None):
        NotificationService.create(user, event_key, title, body, data)

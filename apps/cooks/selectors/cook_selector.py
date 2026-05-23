from apps.cooks.models import CookProfile


def list_cooks():
    return (
        CookProfile.objects.select_related("user")
        .filter(holiday_mode_enabled=False)
        .order_by("-rating")
    )


def get_cook_profile(user_id):
    return CookProfile.objects.select_related("user").filter(user_id=user_id).first()

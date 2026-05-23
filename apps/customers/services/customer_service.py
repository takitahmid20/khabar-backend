from django.db import transaction

from apps.customers.models import CustomerProfile
from apps.users.models import User


class CustomerOnboardingService:
    @staticmethod
    def _get_or_create_profile(user: User) -> CustomerProfile:
        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    @transaction.atomic
    def update_profile(user: User, display_name: str, avatar_url: str | None) -> User:
        user.display_name = display_name
        if avatar_url:
            user.avatar_url = avatar_url
        user.onboarding_step = "complete"
        user.save(update_fields=["display_name", "avatar_url", "onboarding_step", "updated_at"])
        CustomerOnboardingService._get_or_create_profile(user)
        return user

    @staticmethod
    @transaction.atomic
    def complete(user: User) -> User:
        user.onboarding_completed = True
        user.save(update_fields=["onboarding_completed", "updated_at"])
        return user

from django.db import transaction

from apps.cooks.models import CookProfile
from apps.users.models import User
from core.exceptions import ServiceException


class CookOnboardingService:
    @staticmethod
    def _get_or_create_profile(user: User) -> CookProfile:
        profile, _ = CookProfile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    @transaction.atomic
    def update_name(user: User, display_name: str) -> User:
        user.display_name = display_name
        user.onboarding_step = "profile"
        user.save(update_fields=["display_name", "onboarding_step", "updated_at"])
        CookOnboardingService._get_or_create_profile(user)
        return user

    @staticmethod
    @transaction.atomic
    def update_profile(user: User, data: dict) -> CookProfile:
        profile = CookOnboardingService._get_or_create_profile(user)
        profile.bio = data.get("bio")
        profile.cuisine_types = data.get("cuisineTypes", [])
        if data.get("avatarUrl"):
            user.avatar_url = data.get("avatarUrl")
            user.save(update_fields=["avatar_url", "updated_at"])
        profile.save(update_fields=["bio", "cuisine_types", "updated_at"])
        user.onboarding_step = "specialties"
        user.save(update_fields=["onboarding_step", "updated_at"])
        return profile

    @staticmethod
    @transaction.atomic
    def update_specialties(user: User, specialties: list[str], capacity_per_day: int | None = None) -> CookProfile:
        profile = CookOnboardingService._get_or_create_profile(user)
        profile.specialties = specialties
        update_fields = ["specialties", "updated_at"]
        if capacity_per_day is not None:
            profile.capacity_per_day = capacity_per_day
            update_fields.append("capacity_per_day")
        profile.save(update_fields=update_fields)
        user.onboarding_step = "serviceArea"
        user.save(update_fields=["onboarding_step", "updated_at"])
        return profile

    @staticmethod
    @transaction.atomic
    def update_service_area(user: User, data: dict) -> CookProfile:
        profile = CookOnboardingService._get_or_create_profile(user)
        profile.area_label = data.get("areaLabel")
        profile.radius_km = data.get("radiusKm")
        profile.coordinates = data.get("coordinates")
        profile.save(update_fields=["area_label", "radius_km", "coordinates", "updated_at"])
        user.onboarding_step = "identity"
        user.save(update_fields=["onboarding_step", "updated_at"])
        return profile

    @staticmethod
    @transaction.atomic
    def update_payout(user: User, data: dict) -> CookProfile:
        profile = CookOnboardingService._get_or_create_profile(user)
        profile.payout_method = data.get("payoutMethod")
        profile.payout_number = data.get("payoutNumber")
        profile.payout_account_name = data.get("payoutAccountName")
        profile.save(update_fields=["payout_method", "payout_number", "payout_account_name", "updated_at"])
        user.onboarding_step = "complete"
        user.save(update_fields=["onboarding_step", "updated_at"])
        return profile

    @staticmethod
    @transaction.atomic
    def complete(user: User) -> User:
        if user.onboarding_step != "complete":
            raise ServiceException(code="ONBOARDING_INCOMPLETE", message="Onboarding incomplete")
        user.onboarding_completed = True
        user.save(update_fields=["onboarding_completed", "updated_at"])
        return user

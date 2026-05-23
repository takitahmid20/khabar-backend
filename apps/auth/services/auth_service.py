from django.db import transaction

from apps.auth.services.otp_service import OTPService
from apps.auth.services.token_service import TokenService
from apps.users.models import User
from core.exceptions import ServiceException
from shared.enums.core import UserRole


class AuthService:
    @staticmethod
    def _check_duplicate_role(method: str, destination: str, role: str) -> None:
        """
        Prevent the same mobile/email from registering as both cook and customer.
        Only blocks if the existing account has completed onboarding (is actually in use).
        """
        existing_user = None
        if method == "mobile":
            existing_user = User.objects.filter(mobile=destination).first()
        elif method == "email":
            existing_user = User.objects.filter(email=destination).first()

        if existing_user and existing_user.role != role and existing_user.onboarding_completed:
            existing_role_label = "cook" if existing_user.role == UserRole.COOK else "customer"
            requested_role_label = "cook" if role == UserRole.COOK else "customer"
            raise ServiceException(
                code="DUPLICATE_ROLE",
                message=(
                    f"This {method} is already registered as a {existing_role_label}. "
                    f"You cannot create a {requested_role_label} account with the same {method}."
                ),
            )

    @staticmethod
    @transaction.atomic
    def verify_and_login(method: str, destination: str, code: str, role: str) -> dict:
        OTPService.verify_otp(method=method, destination=destination, role=role, code=code)

        user = None
        if method == "mobile":
            user = User.objects.filter(mobile=destination).first()
        elif method == "email":
            user = User.objects.filter(email=destination).first()

        is_new_user = False
        if not user:
            # Validate role
            if role not in UserRole.values:
                raise ServiceException(
                    code="VALIDATION_ERROR",
                    message="Please select a valid role (cook or customer).",
                )

            # Check if this mobile/email is already used by a different role
            AuthService._check_duplicate_role(method, destination, role)

            user = User.objects.create_user(
                mobile=destination if method == "mobile" else None,
                email=destination if method == "email" else None,
                role=role,
            )
            is_new_user = True
            user.onboarding_step = "name" if role == UserRole.COOK else "profile"
            user.onboarding_completed = False
            user.save(update_fields=["onboarding_step", "onboarding_completed", "updated_at"])
        else:
            # Existing user trying to log in with a different role
            if user.role != role:
                if user.onboarding_completed:
                    # Only block if the account is actually set up and in use
                    existing_role_label = "cook" if user.role == UserRole.COOK else "customer"
                    requested_role_label = "cook" if role == UserRole.COOK else "customer"
                    raise ServiceException(
                        code="ROLE_MISMATCH",
                        message=(
                            f"This {method} is registered as a {existing_role_label}. "
                            f"Please sign in as a {existing_role_label} instead, "
                            f"or use a different {method} for your {requested_role_label} account."
                        ),
                    )
                else:
                    # User never completed onboarding — allow role switch
                    user.role = role
                    user.onboarding_step = "name" if role == UserRole.COOK else "profile"
                    user.onboarding_completed = False
                    user.save(update_fields=["role", "onboarding_step", "onboarding_completed", "updated_at"])
                    is_new_user = True

        tokens = TokenService.issue_tokens(user)
        return {
            "accessToken": tokens["accessToken"],
            "refreshToken": tokens["refreshToken"],
            "isNewUser": is_new_user,
            "onboardingCompleted": user.onboarding_completed,
            "user": user,
        }

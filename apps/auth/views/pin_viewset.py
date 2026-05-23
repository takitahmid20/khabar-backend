from rest_framework import permissions, viewsets

from apps.auth.services.token_service import TokenService
from apps.users.models import User
from apps.users.serializers.user_serializer import UserSerializer
from core.exceptions import ServiceException
from core.utils import success_response


class PinViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ("set_pin", "change_pin"):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def login(self, request):
        """Login with PIN instead of OTP."""
        method = request.data.get("method", "mobile")
        destination = request.data.get("destination", "").strip()
        pin = request.data.get("pin", "").strip()
        role = request.data.get("role", "")

        if not destination or not pin:
            raise ServiceException(
                code="VALIDATION_ERROR",
                message="Please provide your phone number and PIN.",
            )

        if len(pin) != 4 or not pin.isdigit():
            raise ServiceException(
                code="VALIDATION_ERROR",
                message="PIN must be exactly 4 digits.",
            )

        # Find user
        user = None
        if method == "mobile":
            user = User.objects.filter(mobile=destination).first()
        elif method == "email":
            user = User.objects.filter(email=destination).first()

        if not user:
            raise ServiceException(
                code="USER_NOT_FOUND",
                message="No account found with this number. Please sign up first.",
            )

        if role and user.role != role:
            raise ServiceException(
                code="ROLE_MISMATCH",
                message=f"This number is registered as a {user.role}. Please select the correct role.",
            )

        if not user.has_pin:
            raise ServiceException(
                code="PIN_NOT_SET",
                message="PIN login is not set up for this account. Please use OTP to sign in.",
            )

        if not user.check_pin(pin):
            raise ServiceException(
                code="PIN_INVALID",
                message="Incorrect PIN. Please try again.",
            )

        tokens = TokenService.issue_tokens(user)
        return success_response({
            "accessToken": tokens["accessToken"],
            "refreshToken": tokens["refreshToken"],
            "isNewUser": False,
            "onboardingCompleted": user.onboarding_completed,
            "user": UserSerializer(user).data,
        })

    def set_pin(self, request):
        """Set a new PIN (for users who don't have one yet)."""
        pin = request.data.get("pin", "").strip()

        if len(pin) != 4 or not pin.isdigit():
            raise ServiceException(
                code="VALIDATION_ERROR",
                message="PIN must be exactly 4 digits.",
            )

        user = request.user
        if user.has_pin:
            raise ServiceException(
                code="PIN_ALREADY_SET",
                message="You already have a PIN. Use change PIN to update it.",
            )

        user.set_pin(pin)
        user.save(update_fields=["pin_hash", "updated_at"])
        return success_response({"hasPin": True}, message="PIN set successfully")

    def change_pin(self, request):
        """Change existing PIN (requires current PIN for verification)."""
        current_pin = request.data.get("currentPin", "").strip()
        new_pin = request.data.get("newPin", "").strip()

        if len(new_pin) != 4 or not new_pin.isdigit():
            raise ServiceException(
                code="VALIDATION_ERROR",
                message="New PIN must be exactly 4 digits.",
            )

        user = request.user
        if not user.has_pin:
            raise ServiceException(
                code="PIN_NOT_SET",
                message="You don't have a PIN set. Use set PIN instead.",
            )

        if not user.check_pin(current_pin):
            raise ServiceException(
                code="PIN_INVALID",
                message="Current PIN is incorrect.",
            )

        user.set_pin(new_pin)
        user.save(update_fields=["pin_hash", "updated_at"])
        return success_response({"hasPin": True}, message="PIN changed successfully")

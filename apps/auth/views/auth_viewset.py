from rest_framework import permissions, status, viewsets

from apps.auth.serializers.otp_send_serializer import OtpSendSerializer
from apps.auth.serializers.otp_verify_serializer import OtpVerifySerializer
from apps.auth.serializers.token_refresh_serializer import TokenRefreshSerializer
from apps.auth.services.auth_service import AuthService
from apps.auth.services.otp_service import OTPService
from apps.auth.services.token_service import TokenService
from apps.users.models import User
from apps.users.serializers.user_serializer import UserSerializer
from core.utils import success_response


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def check_user(self, request):
        """Check if a user exists with the given mobile/email and what login methods are available."""
        method = request.data.get("method", "mobile")
        destination = request.data.get("destination", "").strip()
        role = request.data.get("role", "")

        if not destination:
            return success_response({
                "exists": False,
                "hasPin": False,
                "onboardingCompleted": False,
            })

        user = None
        if method == "mobile":
            user = User.objects.filter(mobile=destination).first()
        elif method == "email":
            user = User.objects.filter(email=destination).first()

        if not user:
            return success_response({
                "exists": False,
                "hasPin": False,
                "onboardingCompleted": False,
            })

        # Check role match
        if role and user.role != role:
            return success_response({
                "exists": False,
                "hasPin": False,
                "onboardingCompleted": False,
            })

        return success_response({
            "exists": True,
            "hasPin": user.has_pin,
            "onboardingCompleted": user.onboarding_completed,
            "displayName": user.display_name,
        })

    def send_otp(self, request):
        serializer = OtpSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = OTPService.send_otp(**serializer.validated_data)
        return success_response(result)

    def verify_otp(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = AuthService.verify_and_login(**serializer.validated_data)
        result["user"] = UserSerializer(result["user"]).data
        return success_response(result)

    def refresh_token(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = TokenService.refresh_tokens(serializer.validated_data["refreshToken"])
        return success_response(tokens)

    def logout(self, request):
        return success_response({}, status_code=status.HTTP_204_NO_CONTENT)

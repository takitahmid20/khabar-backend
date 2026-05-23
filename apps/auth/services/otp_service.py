import secrets
from datetime import timedelta

from django.utils import timezone

from apps.auth.models import OTP
from core.exceptions import ServiceException

OTP_EXPIRY_SECONDS = 120
OTP_COOLDOWN_SECONDS = 22
MAX_ATTEMPTS = 5


class OTPService:
    @staticmethod
    def send_otp(method: str, destination: str, role: str) -> dict:
        # No role-blocking at OTP-send time. The duplicate-role check happens
        # at verify_and_login (account creation) to prevent spam-blocking attacks
        # where someone requests OTPs with your number under a different role
        # just to block you from signing up.

        # Delete any existing OTPs for this method+destination+role so the table
        # doesn't accumulate rows. Only one active OTP per identity at a time.
        OTP.objects.filter(method=method, destination=destination, role=role).delete()

        code = "".join(str(secrets.randbelow(10)) for _ in range(6))
        expires_at = timezone.now() + timedelta(seconds=OTP_EXPIRY_SECONDS)
        OTP.objects.create(
            method=method,
            destination=destination,
            role=role,
            code=code,
            expires_at=expires_at,
        )
        return {
            "message": "OTP sent",
            "expiresInSeconds": OTP_EXPIRY_SECONDS,
            "cooldownSeconds": OTP_COOLDOWN_SECONDS,
        }

    @staticmethod
    def verify_otp(method: str, destination: str, role: str, code: str) -> OTP:
        otp = (
            OTP.objects.filter(method=method, destination=destination, role=role)
            .order_by("-created_at")
            .first()
        )
        if not otp:
            raise ServiceException(
                code="OTP_INVALID",
                message="The verification code is incorrect. Please check and try again.",
            )
        if otp.is_used:
            raise ServiceException(
                code="OTP_INVALID",
                message="This code has already been used. Please request a new one.",
            )
        if otp.attempts >= MAX_ATTEMPTS:
            raise ServiceException(
                code="OTP_TOO_MANY_ATTEMPTS",
                message="Too many incorrect attempts. Please request a new code.",
            )
        if otp.is_expired():
            raise ServiceException(
                code="OTP_EXPIRED",
                message="This code has expired. Please request a new one.",
            )
        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts", "updated_at"])
            remaining = MAX_ATTEMPTS - otp.attempts
            raise ServiceException(
                code="OTP_INVALID",
                message=(
                    f"Incorrect code. You have {remaining} "
                    f"{'attempt' if remaining == 1 else 'attempts'} remaining."
                ),
            )
        otp.is_used = True
        otp.save(update_fields=["is_used", "updated_at"])
        return otp

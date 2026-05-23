from rest_framework import permissions, status, viewsets

from apps.cooks.serializers.onboarding_serializer import (
    CookOnboardingNameSerializer,
    CookOnboardingPayoutSerializer,
    CookOnboardingProfileSerializer,
    CookOnboardingServiceAreaSerializer,
    CookOnboardingSpecialtiesSerializer,
)
from apps.cooks.services.onboarding_service import CookOnboardingService
from apps.cooks.services.verification_service import VerificationService
from core.utils import success_response


class CookOnboardingViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def set_name(self, request):
        serializer = CookOnboardingNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CookOnboardingService.update_name(request.user, serializer.validated_data["displayName"])
        return success_response({"displayName": user.display_name}, message="Name saved")

    def profile(self, request):
        serializer = CookOnboardingProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = CookOnboardingService.update_profile(request.user, serializer.validated_data)
        return success_response({"id": str(profile.id)}, message="Profile saved")

    def specialties(self, request):
        serializer = CookOnboardingSpecialtiesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = CookOnboardingService.update_specialties(
            request.user,
            serializer.validated_data["specialties"],
            capacity_per_day=serializer.validated_data.get("capacityPerDay"),
        )
        return success_response({"id": str(profile.id)}, message="Specialties saved")

    def service_area(self, request):
        serializer = CookOnboardingServiceAreaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = CookOnboardingService.update_service_area(request.user, serializer.validated_data)
        return success_response({"id": str(profile.id)}, message="Service area saved")

    def identity(self, request):
        verification = VerificationService.submit_documents(
            request.user,
            request.FILES.get("nidFront"),
            request.FILES.get("nidBack"),
            request.FILES.get("selfie"),
        )
        return success_response({"status": verification.status}, message="Documents submitted")

    def payout(self, request):
        serializer = CookOnboardingPayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = CookOnboardingService.update_payout(request.user, serializer.validated_data)
        return success_response({"id": str(profile.id)}, message="Payout saved")

    def complete(self, request):
        user = CookOnboardingService.complete(request.user)
        return success_response({"onboardingCompleted": user.onboarding_completed}, message="Onboarding complete")

    def status(self, request):
        return success_response({"onboardingStep": request.user.onboarding_step})

from django.urls import path

from apps.cooks.views.cook_profile_viewset import CookProfileViewSet
from apps.cooks.views.discovery_viewset import CookDiscoveryViewSet
from apps.cooks.views.onboarding_viewset import CookOnboardingViewSet

onboarding_viewset = CookOnboardingViewSet.as_view({
    "patch": "set_name",
})
profile_viewset = CookProfileViewSet.as_view({
    "get": "retrieve",
    "patch": "partial_update",
})
holiday_viewset = CookProfileViewSet.as_view({
    "patch": "holiday_mode",
})
discovery_viewset = CookDiscoveryViewSet.as_view({
    "get": "list",
})
nearby_viewset = CookDiscoveryViewSet.as_view({
    "get": "nearby",
})
trending_viewset = CookDiscoveryViewSet.as_view({
    "get": "trending",
})
search_viewset = CookDiscoveryViewSet.as_view({
    "get": "search",
})
cook_detail_viewset = CookDiscoveryViewSet.as_view({
    "get": "retrieve",
})

urlpatterns = [
    # Cook onboarding
    path("cook/onboarding/name", onboarding_viewset, name="cook-onboarding-name"),
    path("cook/onboarding/profile", CookOnboardingViewSet.as_view({"patch": "profile"}), name="cook-onboarding-profile"),
    path("cook/onboarding/specialties", CookOnboardingViewSet.as_view({"patch": "specialties"}), name="cook-onboarding-specialties"),
    path("cook/onboarding/service-area", CookOnboardingViewSet.as_view({"patch": "service_area"}), name="cook-onboarding-service-area"),
    path("cook/onboarding/identity", CookOnboardingViewSet.as_view({"post": "identity"}), name="cook-onboarding-identity"),
    path("cook/onboarding/payout", CookOnboardingViewSet.as_view({"patch": "payout"}), name="cook-onboarding-payout"),
    path("cook/onboarding/complete", CookOnboardingViewSet.as_view({"post": "complete"}), name="cook-onboarding-complete"),
    path("cook/onboarding/status", CookOnboardingViewSet.as_view({"get": "status"}), name="cook-onboarding-status"),
    # Cook profile
    path("cook/profile", profile_viewset, name="cook-profile"),
    path("cook/profile/holiday-mode", holiday_viewset, name="cook-holiday"),
    # Cook discovery (public)
    path("cooks", discovery_viewset, name="cooks-list"),
    path("cooks/nearby", nearby_viewset, name="cooks-nearby"),
    path("cooks/trending", trending_viewset, name="cooks-trending"),
    path("cooks/search", search_viewset, name="cooks-search"),
    path("cooks/<uuid:pk>", cook_detail_viewset, name="cooks-detail"),
]

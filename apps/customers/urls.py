from django.urls import path

from apps.customers.views.customer_viewset import CustomerOnboardingViewSet, CustomerProfileViewSet

urlpatterns = [
    path("customer/profile", CustomerProfileViewSet.as_view({"get": "retrieve"}), name="customer-profile"),
    path("customer/onboarding/profile", CustomerOnboardingViewSet.as_view({"patch": "profile"}), name="customer-onboarding"),
    path("customer/onboarding/complete", CustomerOnboardingViewSet.as_view({"post": "complete"}), name="customer-onboarding-complete"),
]

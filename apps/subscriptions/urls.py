from django.urls import path

from apps.subscriptions.views.subscription_viewset import SubscriptionViewSet, CookSubscriptionViewSet

urlpatterns = [
    # Customer subscriptions
    path("customer/subscriptions", SubscriptionViewSet.as_view({"get": "list"}), name="subscriptions"),
    path("customer/subscriptions/<uuid:pk>", SubscriptionViewSet.as_view({"get": "retrieve"}), name="subscription-detail"),
    path("customer/subscriptions/<uuid:pk>/calendar", SubscriptionViewSet.as_view({"get": "calendar"}), name="subscription-calendar"),
    path("customer/subscriptions/<uuid:pk>/pause", SubscriptionViewSet.as_view({"post": "pause"}), name="subscription-pause"),
    path("customer/subscriptions/<uuid:pk>/resume", SubscriptionViewSet.as_view({"post": "resume"}), name="subscription-resume"),
    path("customer/subscriptions/<uuid:pk>/cancel", SubscriptionViewSet.as_view({"post": "cancel"}), name="subscription-cancel"),
    path("customer/subscriptions/<uuid:pk>/deliveries/<uuid:delivery_id>/skip", SubscriptionViewSet.as_view({"post": "skip_delivery"}), name="subscription-delivery-skip"),
    path("customer/subscriptions/<uuid:pk>/deliveries/<uuid:delivery_id>/resume", SubscriptionViewSet.as_view({"post": "resume_delivery"}), name="subscription-delivery-resume"),
    # Cook subscriptions
    path("cook/subscriptions", CookSubscriptionViewSet.as_view({"get": "list"}), name="cook-subscriptions"),
    path("cook/subscriptions/<uuid:pk>", CookSubscriptionViewSet.as_view({"get": "retrieve"}), name="cook-subscription-detail"),
]

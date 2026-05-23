from django.db.models import Count, Q

from rest_framework import permissions, viewsets

from apps.customers.serializers.onboarding_serializer import CustomerOnboardingSerializer
from apps.customers.services.customer_service import CustomerOnboardingService
from apps.orders.models import Order
from apps.subscriptions.models import Subscription
from core.utils import success_response
from shared.enums.core import OrderStatus, SubscriptionStatus


class CustomerOnboardingViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def profile(self, request):
        serializer = CustomerOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomerOnboardingService.update_profile(
            request.user,
            serializer.validated_data["displayName"],
            serializer.validated_data.get("avatarUrl"),
        )
        return success_response({"displayName": user.display_name}, message="Profile saved")

    def complete(self, request):
        user = CustomerOnboardingService.complete(request.user)
        return success_response({"onboardingCompleted": user.onboarding_completed})


class CustomerProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        user = request.user

        # Order stats
        orders = Order.objects.filter(customer=user)
        total_orders = orders.count()
        delivered_orders = orders.filter(status=OrderStatus.DELIVERED).count()

        # Subscription info
        active_sub = None
        try:
            sub = Subscription.objects.filter(
                customer=user, status=SubscriptionStatus.ACTIVE
            ).first()
            if sub:
                active_sub = {
                    "id": str(sub.id),
                    "status": sub.status,
                    "planLabel": getattr(sub, "plan_label", "Active Plan"),
                }
        except Exception:
            pass

        # Reviews count
        review_count = 0
        try:
            from apps.reviews.models import Review
            review_count = Review.objects.filter(customer=user).count()
        except Exception:
            pass

        data = {
            "id": str(user.id),
            "displayName": user.display_name,
            "mobile": user.mobile,
            "email": user.email,
            "avatarUrl": user.avatar_url,
            "verificationStatus": user.verification_status,
            "hasPin": user.has_pin,
            "totalOrders": total_orders,
            "deliveredOrders": delivered_orders,
            "reviewCount": review_count,
            "activeSubscription": active_sub,
        }

        return success_response(data)

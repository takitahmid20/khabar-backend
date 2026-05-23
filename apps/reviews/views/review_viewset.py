from rest_framework import permissions, viewsets

from apps.reviews.selectors.review_selector import list_customer_reviews, list_cook_reviews
from apps.reviews.serializers.review_serializer import ReviewSerializer
from apps.reviews.services.review_service import ReviewService
from core.utils import success_response


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "cook_reviews":
            return [permissions.AllowAny()]
        return [permission() for permission in self.permission_classes]

    def list(self, request):
        reviews = list_customer_reviews(request.user.id)
        return success_response({"reviews": ReviewSerializer(reviews, many=True).data})

    def create(self, request):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = ReviewService.create_review(request.user, serializer.validated_data)
        return success_response(ReviewSerializer(review).data, message="Review created")

    def cook_reviews(self, request, cook_id=None):
        reviews = list_cook_reviews(cook_id)
        return success_response({"reviews": ReviewSerializer(reviews, many=True).data})

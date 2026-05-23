from django.urls import path

from apps.reviews.views.review_viewset import ReviewViewSet

urlpatterns = [
    path("customer/reviews", ReviewViewSet.as_view({"get": "list", "post": "create"}), name="customer-reviews"),
    path("cooks/<uuid:cook_id>/reviews", ReviewViewSet.as_view({"get": "cook_reviews"}), name="cook-reviews"),
]

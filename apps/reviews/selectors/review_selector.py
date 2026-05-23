from apps.reviews.models import Review


def list_customer_reviews(customer_id):
    return Review.objects.filter(customer_id=customer_id).order_by("-created_at")


def list_cook_reviews(cook_id):
    return Review.objects.filter(cook_id=cook_id).order_by("-created_at")

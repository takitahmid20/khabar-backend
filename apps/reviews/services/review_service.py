from apps.reviews.models import Review


class ReviewService:
    @staticmethod
    def create_review(customer, data: dict) -> Review:
        return Review.objects.create(customer=customer, **data)

from apps.customers.models import CustomerProfile


def get_customer_profile(user_id):
    return CustomerProfile.objects.select_related("user").filter(user_id=user_id).first()

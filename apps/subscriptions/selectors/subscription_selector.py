from apps.subscriptions.models import Subscription


def list_subscriptions(customer_id):
    return Subscription.objects.select_related("cook").filter(customer_id=customer_id)


def get_subscription(subscription_id, customer_id=None):
    queryset = Subscription.objects.select_related("cook")
    if customer_id:
        queryset = queryset.filter(customer_id=customer_id)
    return queryset.filter(id=subscription_id).first()

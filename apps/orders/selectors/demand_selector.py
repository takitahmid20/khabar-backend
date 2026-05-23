from datetime import date

from apps.orders.models import DemandItem


def get_cook_demand(user, date_str=None):
    query_date = date.fromisoformat(date_str) if date_str else date.today()
    return DemandItem.objects.filter(cook__user=user, date=query_date).select_related("dish")

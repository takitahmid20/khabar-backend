from django.urls import path

from apps.locations.views.address_viewset import AddressViewSet

urlpatterns = [
    path("customer/addresses", AddressViewSet.as_view({"get": "list", "post": "create"}), name="addresses"),
    path("customer/addresses/<uuid:pk>", AddressViewSet.as_view({"patch": "partial_update", "delete": "destroy"}), name="address-detail"),
    path("customer/addresses/<uuid:pk>/default", AddressViewSet.as_view({"patch": "set_default"}), name="address-default"),
]

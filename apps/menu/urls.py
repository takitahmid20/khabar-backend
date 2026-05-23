from django.urls import path

from apps.menu.views.menu_viewset import MenuViewSet

urlpatterns = [
    path("cook/menu", MenuViewSet.as_view({"get": "list"}), name="cook-menu"),
    path("cook/menu/dishes", MenuViewSet.as_view({"post": "create"}), name="cook-dish-create"),
    path("cook/menu/dishes/<uuid:pk>", MenuViewSet.as_view({"patch": "partial_update", "delete": "destroy"}), name="cook-dish-detail"),
    path("cook/menu/dishes/<uuid:pk>/availability", MenuViewSet.as_view({"patch": "availability"}), name="cook-dish-availability"),
    path("cooks/<uuid:cook_id>/menu", MenuViewSet.as_view({"get": "public_menu"}), name="public-cook-menu"),
]

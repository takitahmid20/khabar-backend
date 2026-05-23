from django.urls import path

from apps.users.views.user_viewset import UserViewSet

user_viewset = UserViewSet.as_view({
    "get": "retrieve",
    "patch": "partial_update",
})

urlpatterns = [
    path("users/me", user_viewset, name="user-profile"),
]

from django.urls import path

from apps.auth.views.auth_viewset import AuthViewSet
from apps.auth.views.pin_viewset import PinViewSet

auth_viewset = AuthViewSet.as_view({
    "post": "send_otp",
})
verify_viewset = AuthViewSet.as_view({
    "post": "verify_otp",
})
refresh_viewset = AuthViewSet.as_view({
    "post": "refresh_token",
})
logout_viewset = AuthViewSet.as_view({
    "post": "logout",
})
check_user_viewset = AuthViewSet.as_view({
    "post": "check_user",
})

urlpatterns = [
    path("auth/check-user", check_user_viewset, name="check-user"),
    path("auth/otp/send", auth_viewset, name="otp-send"),
    path("auth/otp/verify", verify_viewset, name="otp-verify"),
    path("auth/pin/login", PinViewSet.as_view({"post": "login"}), name="pin-login"),
    path("auth/pin/set", PinViewSet.as_view({"post": "set_pin"}), name="pin-set"),
    path("auth/pin/change", PinViewSet.as_view({"post": "change_pin"}), name="pin-change"),
    path("auth/token/refresh", refresh_viewset, name="token-refresh"),
    path("auth/logout", logout_viewset, name="logout"),
]

from django.urls import path

from apps.payments.views.payment_viewset import PaymentViewSet
from apps.payments.views.payment_initiate_viewset import PaymentInitiateViewSet
from apps.payments.views.payment_callback_view import PaymentCallbackView
from apps.payments.webhooks import PaymentWebhookView

urlpatterns = [
    # Cook earnings
    path("cook/earnings/summary", PaymentViewSet.as_view({"get": "earnings_summary"}), name="earnings-summary"),
    path("cook/earnings/trend", PaymentViewSet.as_view({"get": "earnings_trend"}), name="earnings-trend"),
    path("cook/earnings/transactions", PaymentViewSet.as_view({"get": "earnings_transactions"}), name="earnings-transactions"),
    path("cook/earnings/withdraw", PaymentViewSet.as_view({"post": "withdraw"}), name="withdraw"),
    path("cook/earnings/withdrawals", PaymentViewSet.as_view({"get": "earnings_transactions"}), name="withdrawals"),
    # Payment initiation
    path("payments/initiate", PaymentInitiateViewSet.as_view({"post": "initiate"}), name="payment-initiate"),
    # Payment callbacks from aamarpay
    path("payments/callback/success", PaymentCallbackView.as_view(), name="payment-callback-success"),
    path("payments/callback/fail", PaymentCallbackView.as_view(), name="payment-callback-fail"),
    path("payments/callback/cancel", PaymentCallbackView.as_view(), name="payment-callback-cancel"),
    # Legacy webhook
    path("webhooks/payment", PaymentWebhookView.as_view(), name="payment-webhook"),
]

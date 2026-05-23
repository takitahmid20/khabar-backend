from django.contrib import admin

from apps.payments.models import Payment, Withdrawal


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "status", "amount", "transaction_id")


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ("id", "cook", "status", "amount")

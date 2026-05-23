from django.db import models


class UserRole(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    COOK = "cook", "Cook"


class VerificationStatus(models.TextChoices):
    UNVERIFIED = "unverified", "Unverified"
    PENDING_REVIEW = "pending_review", "Pending review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class MealSlot(models.TextChoices):
    BREAKFAST = "Breakfast", "Breakfast"
    LUNCH = "Lunch", "Lunch"
    DINNER = "Dinner", "Dinner"


class DayKey(models.TextChoices):
    MON = "mon", "Mon"
    TUE = "tue", "Tue"
    WED = "wed", "Wed"
    THU = "thu", "Thu"
    FRI = "fri", "Fri"
    SAT = "sat", "Sat"
    SUN = "sun", "Sun"


class PlanType(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    TODAY = "today", "Today"


class OrderStatus(models.TextChoices):
    PENDING_PAYMENT = "pending_payment", "Pending payment"
    CONFIRMED = "confirmed", "Confirmed"
    PREPARING = "preparing", "Preparing"
    PACKED = "packed", "Packed"
    OUT_FOR_DELIVERY = "outForDelivery", "Out for delivery"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    CANCELLED = "cancelled", "Cancelled"


class DeliveryStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    DELIVERED = "delivered", "Delivered"
    SKIPPED = "skipped", "Skipped"
    SKIPPED_PAUSED = "skipped_paused", "Skipped paused"


class DemandStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PREPARING = "preparing", "Preparing"
    PACKED = "packed", "Packed"
    OUT_FOR_DELIVERY = "outForDelivery", "Out for delivery"
    DELIVERED = "delivered", "Delivered"


class PaymentMethod(models.TextChoices):
    BKASH = "bkash", "bKash"
    NAGAD = "nagad", "Nagad"
    CARD = "card", "Card"
    BANK = "bank", "Bank"


class WithdrawalStatus(models.TextChoices):
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"

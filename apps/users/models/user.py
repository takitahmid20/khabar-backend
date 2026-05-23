import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from shared.enums.core import UserRole, VerificationStatus


class UserManager(BaseUserManager):
    def create_user(self, mobile=None, email=None, role=UserRole.CUSTOMER, password=None, **extra_fields):
        if not mobile and not email:
            raise ValueError("User must have mobile or email")

        email = self.normalize_email(email) if email else None
        user = self.model(mobile=mobile, email=email, role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not email:
            raise ValueError("Superuser must have email")
        return self.create_user(email=email, password=password, role=UserRole.CUSTOMER, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    mobile = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=120, null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    pin_hash = models.CharField(max_length=128, null=True, blank=True, help_text="Hashed 4-digit PIN for quick login")
    verification_status = models.CharField(
        max_length=30,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
    )
    onboarding_completed = models.BooleanField(default=False)
    onboarding_step = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def has_pin(self) -> bool:
        return bool(self.pin_hash)

    def set_pin(self, raw_pin: str) -> None:
        """Hash and store a 4-digit PIN."""
        import hashlib
        self.pin_hash = hashlib.sha256(raw_pin.encode()).hexdigest()

    def check_pin(self, raw_pin: str) -> bool:
        """Verify a raw PIN against the stored hash."""
        import hashlib
        if not self.pin_hash:
            return False
        return self.pin_hash == hashlib.sha256(raw_pin.encode()).hexdigest()

    def __str__(self):
        return self.display_name or self.email or self.mobile or str(self.id)

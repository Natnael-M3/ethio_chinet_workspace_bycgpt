from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
import uuid


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, first_name=None, last_name=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")

        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # OTP-only users

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        return self.create_user(
            phone_number,
            password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    )

    phone_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=255,null=True, blank=True)
    last_name = models.CharField(max_length=255,null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )

    status = models.CharField(
        max_length=20,
        choices=(('active', 'Active'), ('suspended', 'Suspended')),
        default='active'
    )

    driver_license = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )


    # 🔐 Django auth fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Token auth
    auth_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        null=True,
        blank=True
    )

    # 📍 Location tracking
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # REQUIRED BY DJANGO
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.phone_number

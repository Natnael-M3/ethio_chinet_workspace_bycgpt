from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # OTP & Auth
    OTPSignUpAPIView,
    OTPLoginAPIView,
    VerifyOTPView,
    LogoutView,

    # Admin
    AdminLoginAPIView,
    AdminUserStatusUpdateView,
    AdminRegisterCustomerView,

    # Driver
    UpdateDriverLocationView,

    # ViewSets
    UserViewSet,
)

# -----------------------------
# ROUTER
# -----------------------------
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

# -----------------------------
# URL PATTERNS
# -----------------------------
urlpatterns = [

    # =========================
    # OTP FLOW (Customer / Driver)
    # =========================
    path("signup/", OTPSignUpAPIView.as_view(), name="otp-signup"),
    path("login/", OTPLoginAPIView.as_view(), name="otp-login"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # =========================
    # ADMIN AUTH
    # =========================
    path("admin/login/", AdminLoginAPIView.as_view(), name="admin-login"),

    # =========================
    # DRIVER FEATURES
    # =========================
    path(
        "driver/update-location/",
        UpdateDriverLocationView.as_view(),
        name="driver-update-location"
    ),

    # =========================
    # ADMIN PRIVILEGES
    # =========================
    path(
        "admin/users/<int:id>/status/",
        AdminUserStatusUpdateView.as_view(),
        name="admin-user-status-update"
    ),

    # =========================
    # USER CRUD (ADMIN ONLY)
    # =========================
    path("", include(router.urls)),
]

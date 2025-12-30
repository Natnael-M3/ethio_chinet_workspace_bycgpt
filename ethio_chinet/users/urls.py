from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .views import AdminUserStatusUpdateView
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]

from .views import (
    OTPSignUpAPIView,
    OTPLoginAPIView,
    VerifyOTPView,
    OTPLoginAPIView,
    AdminLoginAPIView,
    UpdateDriverLocationView,
    LogoutView, 
)
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
urlpatterns = [
    # OTP FLOW (Customer / Driver)
    
    path("signup/", OTPSignUpAPIView.as_view(), name="otp_signup"),
    path("login/", OTPLoginAPIView.as_view(), name="otp_login"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # ADMIN LOGIN
    path('admin/login/', AdminLoginAPIView.as_view(), name='admin-login'),

    # Driver utilities
    path('driver/update-location/', UpdateDriverLocationView.as_view()),
    path('', include(router.urls)),
    # ADMIN privilege
    path(
        "admin/users/<int:id>/status/",
        AdminUserStatusUpdateView.as_view(),
        name="admin-user-status-update"
    )
]

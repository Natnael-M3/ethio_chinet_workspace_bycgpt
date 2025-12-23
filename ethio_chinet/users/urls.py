from django.urls import path
from .views import (
    OTPSignUpAPIView,
    OTPLoginAPIView,
    VerifyOTPView,
    OTPLoginAPIView,
    AdminLoginAPIView,
    UpdateDriverLocationView,
    LogoutView, 
)

urlpatterns = [
    # OTP FLOW (Customer / Driver)
  
    path("signup/", OTPSignUpAPIView.as_view(), name="otp_signup"),
    path("login/", OTPLoginAPIView.as_view(), name="otp_login"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # ADMIN LOGIN
    path('admin/login/', AdminLoginAPIView.as_view()),

    # Driver utilities
    path('driver/update-location/', UpdateDriverLocationView.as_view()),
    path('logout/', LogoutView.as_view(), name='logout'),

]

from django.urls import path
from .views import (
    AdminRegisterCustomerView,
    AdminVerifyCustomerOTPView,
    AdminLoginCustomerView
)

urlpatterns = [
    path('register-customer/', AdminRegisterCustomerView.as_view()),
    path('login-customer/', AdminLoginCustomerView.as_view()),
    path('verify-customer-otp/', AdminVerifyCustomerOTPView.as_view()),
]

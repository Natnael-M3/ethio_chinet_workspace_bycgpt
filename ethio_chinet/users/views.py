import uuid
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import SendOTPSerializer
from .serializers import VerifyOTPSerializer
from rest_framework.permissions import AllowAny
import random
from rest_framework.permissions import IsAuthenticated  # <--- import this


# users/views.py
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import SendOTPSerializer, VerifyOTPSerializer

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class OTPSignUpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        if not first_name or not last_name:
            return Response(
                {"error": "first_name and last_name are required for signup."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(phone_number=phone).exists():
            return Response(
                {"message": "Customer already registered. Use login with OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create(
            phone_number=phone,
            first_name=first_name,
            last_name=last_name,
            user_type="customer"
        )
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save()
        print(f"Generated OTP for {phone}: {otp}")  # for testing
        return Response({"message": "OTP sent for signup"}, status=200)


class OTPLoginAPIView(APIView):
    permission_classes = [AllowAny]  # <-- important

    def post(self, request):
        phone = request.data.get('phone_number')
        if not phone:
            return Response(
                {"detail": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "First, you must register using signup."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate OTP for login
        otp = random.randint(100000, 999999)
        user.otp = otp
        user.save()
        print(f"Generated OTP for login {phone}: {otp}")  # For testing

        return Response(
            {"message": "OTP sent for login"},
            status=status.HTTP_200_OK
        )
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response(
                {"message": "First, you need to register."},
                status=status.HTTP_404_NOT_FOUND
            )

        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save()
        print(f"Generated OTP for {phone}: {otp}")  # for testing
        return Response({"message": "OTP sent for login"}, status=200)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        otp = str(serializer.validated_data['otp'])

        try:
            user = User.objects.get(phone_number=phone, otp=otp)
        except User.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        user.otp = None
        user.is_logged_in = True
        user.save()

        tokens = get_tokens_for_user(user)
        return Response({
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user_type": user.user_type
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_logged_in = False
        user.save()
        return Response({"message": "Logged out successfully"})

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_logged_in = False
        user.save()
        return Response({"message": "Logged out successfully"})


class UpdateDriverLocationView(APIView):
    def post(self, request):
        if request.user.user_type != 'driver':
            return Response(
                {"error": "Driver access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        lat = request.data.get('latitude')
        lon = request.data.get('longitude')

        if lat is None or lon is None:
            return Response(
                {"error": "latitude and longitude required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.current_latitude = lat
        request.user.current_longitude = lon
        request.user.location_updated_at = timezone.now()
        request.user.save()

        return Response({"message": "Location updated"})



# class AdminLoginAPIView(APIView):
#     def post(self, request):
#         phone = request.data.get('phone_number')
#         password = request.data.get('password')

#         user = authenticate(
#             request,
#             username=phone,
#             password=password
#         )

#         if not user:
#             return Response(
#                 {"detail": "Invalid credentials"},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )

#         if not user.is_staff:
#             return Response(
#                 {"detail": "Admin access only"},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         refresh = RefreshToken.for_user(user)

#         return Response({
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#             "user_type": user.user_type
#         })

# users/views.py (ADD BELOW your existing views)



# class OTPLoginAPIView(APIView):
#     """
#     Used by Customer & Driver AFTER OTP verification
#     """
#     def post(self, request):
#         phone = request.data.get('phone_number')

#         if not phone:
#             return Response(
#                 {"detail": "Phone number is required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             user = User.objects.get(phone_number=phone)
#         except User.DoesNotExist:
#             return Response(
#                 {"detail": "User not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         refresh = RefreshToken.for_user(user)

#         return Response({
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#             "user_type": user.user_type
#         })
# users/views.py (ADD BELOW OTPLoginAPIView)



class AdminLoginAPIView(APIView):
    """
    Admin login using phone number + password
    """
    def post(self, request):
        phone = request.data.get('phone_number')
        password = request.data.get('password')

        if not phone or not password:
            return Response(
                {"detail": "Phone number and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request,
            username=phone,
            password=password
        )

        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_staff:
            return Response(
                {"detail": "Admin access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_type": user.user_type
        })

import uuid
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import SendOTPSerializer, VerifyOTPSerializer
import random
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, permissions
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404
from .serializers import UserStatusUpdateSerializer
from .permissions import IsAdminUserCustom
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, permissions
from .serializers import AdminRegisterCustomerSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminVerifyCustomerOTPSerializer
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

# -----------------------------
# Signup with OTP generation
# -----------------------------
class OTPSignUpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        user_type = request.data.get("user_type", "customer")  # default to customer

        if not first_name or not last_name:
            return Response(
                {"error": "first_name and last_name are required for signup."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user_type == "admin":
            return Response(
                 {"error":"you can't make user type admin"},
                 status=status.HTTP_400_BAD_REQUEST
            )
        if user_type not in ["customer", "driver"]:
            return Response(
                 {"error": "user_type must be either 'customer' or 'driver'"},
                 status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(phone_number=phone).exists():
            return Response(
                {"message": "User already registered. Use login with OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user
        user = User.objects.create(
            phone_number=phone,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )

        # Generate OTP and save
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save()

        print(f"Generated OTP for {phone}: {otp}")  # testing purpose

        return Response({"message": "OTP sent for signup"}, status=status.HTTP_200_OK)

# -----------------------------
# Login OTP generation
# -----------------------------
class OTPLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found. First, you need to signup."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate OTP and save
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save()

        print(f"Generated OTP for login {phone}: {otp}")  # testing

        return Response({"message": "OTP sent for login"}, status=status.HTTP_200_OK)

# -----------------------------
# OTP verification
# -----------------------------
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = {
            "detail": "Customer verified successfully",
            "customer_id": user.id,
            "phone_number": user.phone_number
        }

        # ✅ issue tokens ONLY if requested (mobile app)
        if request.data.get("issue_token", False):
            refresh = RefreshToken.for_user(user)
            response["access"] = str(refresh.access_token)
            response["refresh"] = str(refresh)

        return Response(response, status=status.HTTP_200_OK)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        print(refresh_token)
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"success": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)



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


    def post(self, request):
        phone = request.data.get('phone_number')
        password = request.data.get('password')

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
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    # optionally, restrict some actions to admin only
    def get_permissions(self):
        if self.action in ['partial_update', 'update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
class AdminUserStatusUpdateView(APIView):
    permission_classes = [IsAdminUserCustom]
    def patch(self, request, id):
        print("🔥 PATCH CALLED")
    def patch(self, request, id):
        user = get_object_or_404(User, id=id)

        # ❌ Admin cannot suspend another admin
        if user.is_staff:
            return Response(
                {"detail": "You cannot change admin status."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserStatusUpdateSerializer(
            user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "User status updated successfully",
                    "user_id": user.id,
                    "status": user.status
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    AdminRegisterCustomerSerializer,
    VerifyOTPSerializer
)


class AdminRegisterCustomerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminRegisterCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Customer registered successfully. OTP sent.",
                "phone_number": user.phone_number
            },
            status=status.HTTP_201_CREATED
        )

class AdminVerifyCustomerOTPView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminVerifyCustomerOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Customer verified successfully by admin",
                "customer_id": user.id,
                "phone_number": user.phone_number
            },
            status=status.HTTP_200_OK
        )
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminLoginCustomerSerializer

class AdminLoginCustomerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminLoginCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "OTP sent to customer phone number",
                "customer_id": user.id,
                "phone_number": user.phone_number
            },
            status=status.HTTP_200_OK
        )


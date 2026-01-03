import random
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate

from .models import User
from .permissions import IsAdminUserCustom
from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    UserSerializer,
    UserStatusUpdateSerializer,
    AdminRegisterCustomerSerializer,
    AdminVerifyCustomerOTPSerializer,
    AdminLoginCustomerSerializer,
)

# --------------------------------------------------
# TOKEN HELPER
# --------------------------------------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

# --------------------------------------------------
# SIGNUP WITH OTP
# --------------------------------------------------
class OTPSignUpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        user_type = request.data.get("user_type", "customer")

        if not first_name or not last_name:
            return Response(
                {"error": "first_name and last_name are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_type == "admin":
            return Response(
                {"error": "Cannot create admin via signup"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_type not in ["customer", "driver"]:
            return Response(
                {"error": "user_type must be customer or driver"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(phone_number=phone).exists():
            return Response(
                {"message": "User already exists. Use login OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create(
            phone_number=phone,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            is_online=False
        )

        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save()

        print(f"[SIGNUP OTP] {phone}: {otp}")

        return Response(
            {"message": "OTP sent for signup"},
            status=status.HTTP_200_OK
        )

# --------------------------------------------------
# LOGIN OTP
# --------------------------------------------------
class OTPLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']
        user = get_object_or_404(User, phone_number=phone)

        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save(update_fields=["otp"])

        print(f"[LOGIN OTP] {phone}: {otp}")

        return Response(
            {"message": "OTP sent for login"},
            status=status.HTTP_200_OK
        )

# --------------------------------------------------
# VERIFY OTP (LOGIN / SIGNUP)
# --------------------------------------------------
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # ✅ ONLINE
        user.is_online = True
        user.last_seen = timezone.now()
        user.save(update_fields=["is_online", "last_seen"])

        response = {
            "detail": "Verified successfully",
            "user_id": user.id,
            "phone_number": user.phone_number,
            "user_type": user.user_type,
        }

        if request.data.get("issue_token", False):
            tokens = get_tokens_for_user(user)
            response.update(tokens)

        return Response(response, status=status.HTTP_200_OK)

# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            # 🔴 OFFLINE
            request.user.is_online = False
            request.user.last_seen = timezone.now()
            request.user.save(update_fields=["is_online", "last_seen"])

            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )

# --------------------------------------------------
# DRIVER LOCATION (AUTO ONLINE)
# --------------------------------------------------
class UpdateDriverLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != "driver":
            return Response(
                {"error": "Driver access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        lat = request.data.get("latitude")
        lon = request.data.get("longitude")

        if lat is None or lon is None:
            return Response(
                {"error": "latitude & longitude required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.current_latitude = lat
        request.user.current_longitude = lon
        request.user.location_updated_at = timezone.now()

        # 🟢 driver is online
        request.user.is_online = True
        request.user.last_seen = timezone.now()

        request.user.save()

        return Response({"message": "Location updated"})

# --------------------------------------------------
# ADMIN LOGIN (PASSWORD)
# --------------------------------------------------
class AdminLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        password = request.data.get("password")

        user = authenticate(request, username=phone, password=password)

        if not user or not user.is_staff:
            return Response(
                {"detail": "Invalid admin credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = get_tokens_for_user(user)

        user.is_online = True
        user.last_seen = timezone.now()
        user.save(update_fields=["is_online", "last_seen"])

        return Response({
            **tokens,
            "user_type": user.user_type
        })

# --------------------------------------------------
# USER CRUD (ADMIN RESTRICTED)
# --------------------------------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()

# --------------------------------------------------
# ADMIN STATUS UPDATE
# --------------------------------------------------
class AdminUserStatusUpdateView(APIView):
    permission_classes = [IsAdminUserCustom]

    def patch(self, request, id):
        user = get_object_or_404(User, id=id)

        if user.is_staff:
            return Response(
                {"detail": "Cannot modify admin"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserStatusUpdateSerializer(
            user, data=request.data, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Status updated",
            "user_id": user.id,
            "status": user.status
        })

# --------------------------------------------------
# ADMIN CUSTOMER FLOWS
# --------------------------------------------------
class AdminRegisterCustomerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminRegisterCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": "Customer registered, OTP sent"},
            status=status.HTTP_201_CREATED
        )

class AdminVerifyCustomerOTPView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminVerifyCustomerOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": "Customer verified"},
            status=status.HTTP_200_OK
        )

class AdminLoginCustomerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminLoginCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": "OTP sent to customer"},
            status=status.HTTP_200_OK
        )

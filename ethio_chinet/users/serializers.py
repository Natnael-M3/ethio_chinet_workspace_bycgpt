from rest_framework import serializers
from .models import User
from django.utils import timezone

import random



class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must be numeric")
        return value

    def save(self):
        phone_number = self.validated_data['phone_number']

        user, _ = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={"user_type": "customer"}
        )

        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.is_verified = False
        user.save(update_fields=["otp", "is_verified"])

        # 📩 send SMS here (mocked for now)
        print(f"Generated OTP for {phone_number}: {otp}")

        return user



class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(phone_number=data['phone_number'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        # ❌ admin must NOT verify with OTP
        if user.user_type == 'admin':
            raise serializers.ValidationError("Admin cannot verify with OTP")

        # if user.is_verified:
        #     raise serializers.ValidationError("User already verified")

        if user.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        # user.is_verified = True
        user.otp = None
        user.save(update_fields=['is_verified', 'otp'])
        return user



class UserSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id',
            'first_name',
            'last_name',
            'phone_number',
            'status',
            'is_staff',
            'user_type',
            'current_latitude',
            'current_longitude',
            'last_seen_at',
            'is_online',]
    def get_is_online(self, obj):
        return obj.is_online
    def update(self, instance, validated_data):
        # Prevent non-admins from updating the status
        request = self.context.get('request')
        if 'status' in validated_data:
            if not request.user.is_staff:  # only admins can change status
                validated_data.pop('status')
        return super().update(instance, validated_data)
class UserStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["status"]

    def validate_status(self, value):
        if value not in ["active", "suspended"]:
            raise serializers.ValidationError(
                "Status must be either 'active' or 'suspended'."
            )
        return value
from rest_framework import serializers
from .models import User

from rest_framework import serializers
from .models import User

class AdminRegisterCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']

    def create(self, validated_data):
        otp = str(random.randint(100000, 999999))

        user, created = User.objects.get_or_create(
            phone_number=validated_data['phone_number'],
            defaults={
                'first_name': validated_data.get('first_name'),
                'last_name': validated_data.get('last_name'),
                'user_type': 'customer',
                'otp': otp,
                'is_verified': False
            }
        )

        if not created:
            user.otp = otp
            user.is_verified = False
            user.save(update_fields=['otp', 'is_verified'])

        # 🔔 replace with SMS later
        print(f"OTP for {user.phone_number}: {otp}")

        return user

class AdminVerifyCustomerOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(
                phone_number=data['phone_number'],
                user_type='customer'
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("Customer not found")

        if user.is_verified:
            raise serializers.ValidationError("Customer already verified")

        if user.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        user.is_verified = True
        user.otp = None
        user.save(update_fields=['is_verified', 'otp'])
        return user

class AdminLoginCustomerSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(
                phone_number=data['phone_number'],
                user_type='customer'
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Customer not registered. Register customer first."
            )

        if user.status == 'suspended':
            raise serializers.ValidationError("Customer is suspended")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save(update_fields=['otp'])

        # TODO: integrate SMS provider
        print(f"[ADMIN LOGIN OTP] {user.phone_number}: {otp}")

        return user
class DriverLocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'current_latitude',
            'current_longitude',
        ]

    def validate(self, data):
        user = self.context['request'].user

        if user.user_type != 'driver':
            raise serializers.ValidationError(
                "Only drivers can update location"
            )

        if user.status != 'active':
            raise serializers.ValidationError(
                "Suspended drivers cannot update location"
            )

        return data

    def update(self, instance, validated_data):
        instance.current_latitude = validated_data.get(
            'current_latitude', instance.current_latitude
        )
        instance.current_longitude = validated_data.get(
            'current_longitude', instance.current_longitude
        )

        # 🔥 heartbeat
        instance.last_seen_at = timezone.now()
        instance.location_updated_at = timezone.now()

        instance.save(
            update_fields=[
                'current_latitude',
                'current_longitude',
                'last_seen_at',
                'location_updated_at'
            ]
        )

        return instance

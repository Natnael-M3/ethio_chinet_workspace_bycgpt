from rest_framework import serializers
from .models import User
import random


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone must be numeric")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    otp = serializers.IntegerField()

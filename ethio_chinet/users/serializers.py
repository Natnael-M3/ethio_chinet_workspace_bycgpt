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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'status', 'is_staff']

    def update(self, instance, validated_data):
        # Prevent non-admins from updating the status
        request = self.context.get('request')
        if 'status' in validated_data:
            if not request.user.is_staff:  # only admins can change status
                validated_data.pop('status')
        return super().update(instance, validated_data)


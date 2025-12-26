from rest_framework import serializers
from .models import Post
import random
import string
from datetime import timedelta
from django.utils import timezone


def generate_post_code():
    return ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'pickup_location',
            'dropoff_location',
            'vehicle_type',
            'load_type',
            'required_date',
        ]

    def validate_required_date(self, value):
        now = timezone.now()

        if value < now + timedelta(hours=2):
            raise serializers.ValidationError(
                "Required date must be at least 2 hours from now"
            )

        if value > now + timedelta(days=3):
            raise serializers.ValidationError(
                "Required date cannot exceed 3 days"
            )

        return value

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        # 🔒 BRD ENFORCEMENT
        if user.user_type != 'customer':
            raise serializers.ValidationError(
                "Only customers can create posts"
            )

        post = Post.objects.create(
            customer=user,
            post_code=generate_post_code(),
            expires_at=validated_data['required_date'],
            **validated_data
        )

        return post


class PostListSerializer(serializers.ModelSerializer):
    pickup_location_name = serializers.CharField(
        source='pickup_location.location_name', read_only=True
    )
    dropoff_location_name = serializers.CharField(
        source='dropoff_location.location_name', read_only=True
    )

    class Meta:
        model = Post
        fields = [
            'id',
            'post_code',
            'pickup_location_name',
            'dropoff_location_name',
            'required_date',
            'status',     
            'is_expired'  
        ]

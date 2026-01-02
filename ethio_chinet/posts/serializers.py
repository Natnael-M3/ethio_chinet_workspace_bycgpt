from rest_framework import serializers
from .models import Post
from loadtypes.models import LoadType
from vehicles.models import VehicleType

from rest_framework import serializers
from .models import Post
from luggages.models import Luggage
from django.utils import timezone
import datetime
from rest_framework import serializers
from .models import Post
from users.models import User
# from loadtypes.models import LoadType
from rest_framework import serializers
from .models import Post
from rest_framework import serializers
from .models import DriverRating, Post
from users.models import User

class PostCreateSerializer(serializers.ModelSerializer):
    luggage = serializers.PrimaryKeyRelatedField(
        queryset=Luggage.objects.all()
    )
    load_type = serializers.PrimaryKeyRelatedField(
        queryset=LoadType.objects.all()
    )

    class Meta:
        model = Post
        fields = [
            'pickup_location',
            'dropoff_location',
            'vehicle_type',
            'load_type',
            'luggage',
            'required_date',
            'description'
        ]

    def validate_required_date(self, value):
        now = timezone.now()
        if value < now + datetime.timedelta(hours=2):
            raise serializers.ValidationError(
                "Required date must be at least 2 hours from now."
            )
        return value



class PostListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)
    assigned_admin_name = serializers.CharField(source='assigned_admin.get_full_name', read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
class PostDriverListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id',
            'post_code',
            'pickup_location',
            'dropoff_location',
            'vehicle_type',
            'load_type',
            'luggage',
            'required_date',
            'status',
        ]



class DriverPostListSerializer(serializers.ModelSerializer):
    pickup_location = serializers.StringRelatedField()
    dropoff_location = serializers.StringRelatedField()
    vehicle_type = serializers.StringRelatedField()
    load_type = serializers.StringRelatedField()
    luggage = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = [
            "id",
            "post_code",
            "pickup_location",
            "dropoff_location",
            "vehicle_type",
            "load_type",
            "luggage",
            "required_date",
            "status",
        ]
        
class DriverFinishedPostSerializer(serializers.ModelSerializer):
    pickup_location = serializers.StringRelatedField()
    dropoff_location = serializers.StringRelatedField()
    luggage = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = [
            "post_code",
            "pickup_location",
            "dropoff_location",
            "luggage",
            "required_date",
            "status",
        ]


from rest_framework import serializers
from posts.models import Post
from users.models import User


class AdminPostForCustomerSerializer(serializers.ModelSerializer):
    customer_phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = Post
        fields = [
            'customer_phone_number',
            'pickup_location',
            'dropoff_location',
            'vehicle_type',
            'load_type',
            'luggage',
            'required_date',
            'description'
        ]

    def validate_customer_phone_number(self, value):
        try:
            customer = User.objects.get(
                phone_number=value,
                user_type='customer'
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "You have to register customer first before posting"
            )
        if customer.otp is not None:
            raise serializers.ValidationError(
                "Customer not verified. Please verify OTP before posting."
            )
        self.context['customer'] = customer
        return value

    def create(self, validated_data):
        customer = self.context['customer']
        validated_data.pop('customer_phone_number')

        post = Post.objects.create(
            customer=customer,
            **validated_data
        )
        return post

class DriverRatingSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)

    class Meta:
        model = DriverRating
        fields = ['driver', 'driver_name', 'success_rate', 'last_updated']
        read_only_fields = ['driver_name', 'success_rate', 'last_updated']

from rest_framework import serializers
from .models import DriverRating, Post
from users.models import User

class DriverRatingSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)

    class Meta:
        model = DriverRating
        fields = ['driver', 'driver_name', 'success_rate', 'last_updated']
        read_only_fields = ['driver_name', 'success_rate', 'last_updated']

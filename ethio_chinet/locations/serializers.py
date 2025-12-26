from rest_framework import serializers
from .models import Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'location_name', 'latitude', 'longitude']

    def validate_location_name(self, value):
        # Check if a location with the same name already exists
        if Location.objects.filter(location_name__iexact=value).exists():
            raise serializers.ValidationError("This location is already added.")
        return value

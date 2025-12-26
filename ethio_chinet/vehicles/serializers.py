from rest_framework import serializers
from .models import Vehicle, VehicleType, VehicleRegion, VehicleCode

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'

class VehicleRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleRegion
        fields = '__all__'

class VehicleCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCode
        fields = '__all__'
class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'vehicle_type', 'vehicle_region', 'vehicle_code', 'load_type', 'capacity_kg']

    def create(self, validated_data):
        user = self.context['request'].user
        if user.user_type != 'driver':
            raise serializers.ValidationError("Only drivers can register vehicles")
        
        # Ensure driver has only one vehicle
        if hasattr(user, 'vehicle'):
            raise serializers.ValidationError("Driver already has a vehicle registered")

        vehicle = Vehicle.objects.create(driver=user, **validated_data)
        return vehicle

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user != instance.driver:
            raise serializers.ValidationError("You can only update your own vehicle")
        return super().update(instance, validated_data)

    
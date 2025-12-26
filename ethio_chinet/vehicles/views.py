from rest_framework import viewsets
from .models import Vehicle, VehicleType, VehicleRegion, VehicleCode
from .serializers import VehicleSerializer, VehicleTypeSerializer, VehicleRegionSerializer, VehicleCodeSerializer
from .permissions import IsAdminUserCustom, IsDriverUser
from rest_framework import generics, permissions
from .models import VehicleType, VehicleRegion, VehicleCode, Vehicle
from rest_framework import serializers
from .models import VehicleType, VehicleRegion, VehicleCode, Vehicle

from .serializers import (
    VehicleTypeSerializer,
    VehicleRegionSerializer,
    VehicleCodeSerializer,
    VehicleSerializer,
)
# Admin-only ViewSets
class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsAdminUserCustom]

class VehicleRegionViewSet(viewsets.ModelViewSet):
    queryset = VehicleRegion.objects.all()
    serializer_class = VehicleRegionSerializer
    permission_classes = [IsAdminUserCustom]

class VehicleCodeViewSet(viewsets.ModelViewSet):
    queryset = VehicleCode.objects.all()
    serializer_class = VehicleCodeSerializer
    permission_classes = [IsAdminUserCustom]

# Driver-only ViewSet
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsDriverUser]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'driver':
            return Vehicle.objects.filter(driver=user)
        return Vehicle.objects.none()  # customers cannot see


from rest_framework import viewsets
from .models import Vehicle, VehicleType, VehicleRegion, VehicleCode
from .serializers import VehicleSerializer, VehicleTypeSerializer, VehicleRegionSerializer, VehicleCodeSerializer
from .permissions import IsAdminUserCustom, IsDriverUser
from rest_framework import generics, permissions
from .models import VehicleType, VehicleRegion, VehicleCode, Vehicle
from rest_framework import serializers
from .models import VehicleType, VehicleRegion, VehicleCode, Vehicle, LoadType

from .serializers import (
    VehicleTypeSerializer,
    VehicleRegionSerializer,
    VehicleCodeSerializer,
    VehicleSerializer,
    LoadTypeSerializer
)

class LoadTypeViewSet(viewsets.ModelViewSet):
    queryset = LoadType.objects.all()
    serializer_class = LoadTypeSerializer
    permission_classes = [IsAdminUserCustom]
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
from rest_framework import viewsets, permissions
from .models import Vehicle
from .serializers import VehicleSerializer

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import Vehicle
from .serializers import VehicleSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # driver sees ONLY their vehicle
        if user.user_type == "driver":
            return Vehicle.objects.filter(driver=user)
        return Vehicle.objects.none()  # safety

    def check_suspended(self, user):
        if user.status == "suspended":
            return Response(
                {"detail": "Your account is suspended"},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    def list(self, request, *args, **kwargs):
        suspended_response = self.check_suspended(request.user)
        if suspended_response:
            return suspended_response
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        suspended_response = self.check_suspended(request.user)
        if suspended_response:
            return suspended_response
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        suspended_response = self.check_suspended(request.user)
        if suspended_response:
            return suspended_response
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        suspended_response = self.check_suspended(request.user)
        if suspended_response:
            return suspended_response
        return super().destroy(request, *args, **kwargs)

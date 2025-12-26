from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Location
from .serializers import LocationSerializer

class IsAdminUserCustom(permissions.BasePermission):
    """
    Custom permission to only allow admin users to create/update/delete.
    """
    def has_permission(self, request, view):
        # Allow everyone to list or retrieve
        if view.action in ['list', 'retrieve']:
            return True
        # Only admin users can create/update/delete
        return request.user.is_staff  # or use your user_type == 'admin' if custom

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAdminUserCustom]

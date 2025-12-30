from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import LoadType
from .serializers import LoadTypeSerializer

class LoadTypeViewSet(viewsets.ModelViewSet):
    queryset = LoadType.objects.all()
    serializer_class = LoadTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

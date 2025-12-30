from rest_framework import viewsets
from .models import Luggage
from .serializers import LuggageSerializer
from vehicles.permissions import IsAdminUserCustom


class LuggageViewSet(viewsets.ModelViewSet):
    queryset = Luggage.objects.all()
    serializer_class = LuggageSerializer
    permission_classes = [IsAdminUserCustom]

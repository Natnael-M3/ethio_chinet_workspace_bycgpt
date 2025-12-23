from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Location


class LocationAutocompleteView(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()

        if len(query) < 2:
            return Response([])

        locations = Location.objects.filter(
            name__icontains=query,
            is_active=True
        )[:10]

        data = [
            {
                "id": loc.id,
                "name": loc.name,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
            }
            for loc in locations
        ]

        return Response(data, status=status.HTTP_200_OK)

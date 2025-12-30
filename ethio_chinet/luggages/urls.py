from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import LuggageViewSet

router = DefaultRouter()
router.register(r'', LuggageViewSet, basename='luggage')

urlpatterns = [
    path('', include(router.urls)),
]

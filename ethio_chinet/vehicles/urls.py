from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleViewSet,
    VehicleTypeViewSet,
    VehicleRegionViewSet,
    VehicleCodeViewSet,
)

router = DefaultRouter()
router.register(r'vehicle-types', VehicleTypeViewSet, basename='vehicle-type')
router.register(r'vehicle-regions', VehicleRegionViewSet, basename='vehicle-region')
router.register(r'vehicle-codes', VehicleCodeViewSet, basename='vehicle-code')
router.register(r'', VehicleViewSet, basename='vehicle')  # driver endpoint

urlpatterns = [
    path('', include(router.urls)),
]

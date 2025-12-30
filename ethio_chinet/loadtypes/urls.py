from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoadTypeViewSet

router = DefaultRouter()
router.register(r'', LoadTypeViewSet, basename='load-type')

urlpatterns = [
    path('', include(router.urls)),
]

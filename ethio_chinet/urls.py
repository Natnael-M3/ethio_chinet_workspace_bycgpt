from django.urls import path, include
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # for access & refresh tokens
    TokenRefreshView,     # for refresh token only
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # POST: get access & refresh tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # POST: refresh access token
    path('api/locations/', include('locations.urls')),  # <-- make sure this line exists
    # Vehicle endpoint
    path('api/vehicles/', include('vehicles.urls')),
    #luggages endpoint
    path('api/luggage/', include('luggages.urls')),
    #load types endpoint
    path('api/load-types/', include('loadtypes.urls')),
    path("api/", include("users.urls")),

]

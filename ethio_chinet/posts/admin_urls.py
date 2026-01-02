# posts/admin_urls.py
from django.urls import path
from .views import AdminPostCustomerView
from django.urls import path
from .views import UpdateDriverRatingView, GetDriverRatingView
urlpatterns = [
    path(
        'postfor-customer/',
        AdminPostCustomerView.as_view(),
        name='admin-post-for-customer'
    ),
    path('update-driver-rating/<int:driver_id>/', UpdateDriverRatingView.as_view(), name='update-driver-rating'),
    path('get-driver-rating/<int:driver_id>/', GetDriverRatingView.as_view(), name='get-driver-rating'),
]




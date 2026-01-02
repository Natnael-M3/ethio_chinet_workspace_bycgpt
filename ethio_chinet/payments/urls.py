from django.urls import path
from .views import AdminRecordPaymentView

urlpatterns = [
    path('record-payment/', AdminRecordPaymentView.as_view()),
]

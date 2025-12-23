from django.urls import path
from .views import RecordFinishedPaymentView

urlpatterns = [
    path('record/<int:post_id>/', RecordFinishedPaymentView.as_view()),
]

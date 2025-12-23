from django.urls import path
from .views import LocationAutocompleteView

urlpatterns = [
    path('autocomplete/', LocationAutocompleteView.as_view()),
]

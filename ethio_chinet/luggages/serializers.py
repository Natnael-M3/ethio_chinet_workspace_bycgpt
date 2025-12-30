from rest_framework import serializers
from .models import Luggage


class LuggageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Luggage
        fields = ['id', 'name']

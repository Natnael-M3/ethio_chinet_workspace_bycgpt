from rest_framework import serializers
from .models import LoadType

class LoadTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadType
        fields = ['id', 'name']

from rest_framework import serializers
from .models import PostPayment


class PostPaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPayment
        fields = ['finished_amount']

    def validate_finished_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Finished amount must be greater than zero."
            )
        return value

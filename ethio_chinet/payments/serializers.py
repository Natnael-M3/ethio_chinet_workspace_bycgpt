from rest_framework import serializers
from posts.models import Post
from .models import Payment


class AdminRecordPaymentSerializer(serializers.Serializer):
    post_code = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        try:
            post = Post.objects.get(post_code=data['post_code'])
        except Post.DoesNotExist:
            raise serializers.ValidationError(
                {"post_code": "Post not found."}
            )

        if post.status.lower() != "finished":
            raise serializers.ValidationError(
                "Payment can only be recorded for finished posts."
            )

        if hasattr(post, 'payment'):
            raise serializers.ValidationError(
                "Payment already recorded for this post."
            )

        data['post'] = post
        return data

    def create(self, validated_data):
        request = self.context['request']

        payment = Payment.objects.create(
            post=validated_data['post'],
            admin=request.user,
            amount=validated_data['amount']
        )
        return payment

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from posts.models import Post
from .models import PostPayment
# from .serializers import PostPaymentSerializer
from .serializers import PostPaymentCreateSerializer


class RecordFinishedPaymentView(APIView):
    def post(self, request, post_id):
        # Admin only
        permission_classes = [IsAdminUser]

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Post must be finished
        if post.status != 'Finished':
            return Response(
                {"error": "Payment can only be recorded for finished posts"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Admin ownership check
        if post.assigned_admin != request.user:
            return Response(
                {"error": "You are not assigned to this post"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Prevent duplicate payment
        if hasattr(post, 'payment'):
            return Response(
                {"error": "Payment already recorded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PostPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        PostPayment.objects.create(
            post=post,
            admin=request.user,
            finished_amount=serializer.validated_data['finished_amount']
        )

        return Response(
            {"message": "Finished payment recorded successfully"},
            status=status.HTTP_201_CREATED
        )

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminRecordPaymentSerializer


class AdminRecordPaymentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminRecordPaymentSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        return Response(
            {
                "message": "Payment recorded successfully",
                "post_code": payment.post.post_code,
                "amount": payment.amount
            },
            status=status.HTTP_201_CREATED
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Post
from .serializers import PostCreateSerializer, PostListSerializer
from users.models import User
from .models import Post
from .serializers import (
    DriverPostListSerializer,
    DriverFinishedPostSerializer,
)
def admin_only(user):
    return user.user_type == 'admin'
def get_serializer_class(self):
    user = self.request.user

    if user.user_type == 'driver':
        return PostDriverListSerializer

    return PostListSerializer
# ------------------- CUSTOMER VIEWS -------------------


    
class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.status == "suspended":
            return Response(
                {
                    "detail": "Your account is suspended. You cannot create posts."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        if request.user.user_type != 'customer':
            return Response({"error": "Only customers can create posts"}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(customer=request.user)
        return Response({"message": "Post created", "post_code": post.post_code}, status=status.HTTP_201_CREATED)

class CustomerPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(customer=request.user)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

# ------------------- ADMIN VIEWS -------------------

class AdminAvailablePostsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not admin_only(request.user):
            return Response({"error": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)
        posts = Post.objects.filter(status='posted')
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

class AdminTakePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        if not admin_only(request.user):
            return Response({"error": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        if post.status != 'posted':
            return Response({"error": "Post is not available"}, status=status.HTTP_400_BAD_REQUEST)

        driver_id = request.data.get('driver_id')
        try:
            driver = User.objects.get(id=driver_id, user_type='driver', status='active')
        except User.DoesNotExist:
            return Response({"error": "Invalid driver"}, status=status.HTTP_400_BAD_REQUEST)

        post.status = 'taken'
        post.driver = driver
        post.assigned_admin = request.user
        post.save()
        return Response({"message": "Post taken successfully"})

class AdminTakenPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not admin_only(request.user):
            return Response({"error": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)
        posts = Post.objects.filter(status='taken')
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

class AdminFinishPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        if not admin_only(request.user):
            return Response({"error": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        if post.status != 'taken':
            return Response({"error": "Post is not in taken state"}, status=status.HTTP_400_BAD_REQUEST)
        if post.assigned_admin != request.user:
            return Response({"error": "You are not assigned to this post"}, status=status.HTTP_403_FORBIDDEN)
        post.status = 'Finished'
        post.save()
        return Response({"message": "Post finished successfully"})

class AdminReleasePostView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        if not admin_only(request.user):
            return Response({"error": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        if post.status != 'taken':
            return Response({"error": "Post is not taken"}, status=status.HTTP_400_BAD_REQUEST)
        if post.assigned_admin != request.user:
            return Response({"error": "You are not assigned to this post"}, status=status.HTTP_403_FORBIDDEN)

        post.status = 'posted'
        post.driver = None
        post.assigned_admin = None
        post.save()
        return Response({"message": "Post released back to available"})



# 🚚 DRIVER: Available Posts
class DriverAvailablePostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type != "driver":
            return Response(
                {"detail": "Driver access only"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.status == "suspended":
            return Response(
                {"detail": "Your account is suspended"},
                status=status.HTTP_403_FORBIDDEN,
            )
        current_vehicle = user.vehicles.first()
        if not current_vehicle:
            return Response(
                {"detail": "No vehicle assigned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        posts = Post.objects.filter(
            status="posted",
            is_expired=False,
            vehicle_type=user.current_vehicle.vehicle_type,
            load_type=user.current_vehicle.load_type,
            required_date__gte=timezone.now(),
        )

        serializer = DriverPostListSerializer(posts, many=True)
        return Response(serializer.data)


# 🚚 DRIVER: Posts Taken by Him
class DriverTakenPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type != "driver":
            return Response(
                {"detail": "Driver access only"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.status == "suspended":
            return Response(
                {"detail": "Your account is suspended"},
                status=status.HTTP_403_FORBIDDEN,
            )

        posts = Post.objects.filter(
            status="taken",
            driver=user,
        )

        serializer = DriverPostListSerializer(posts, many=True)
        return Response(serializer.data)


# 🚚 DRIVER: Finished Posts (HISTORY)
class DriverFinishedPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type != "driver":
            return Response(
                {"detail": "Driver access only"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.status == "suspended":
            return Response(
                {"detail": "Your account is suspended"},
                status=status.HTTP_403_FORBIDDEN,
            )

        posts = Post.objects.filter(
            status="Finished",
            driver=user,
        )

        serializer = DriverFinishedPostSerializer(posts, many=True)
        return Response(serializer.data)

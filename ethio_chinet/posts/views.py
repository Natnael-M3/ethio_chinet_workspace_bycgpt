from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .services import haversine_distance
from .models import Post
from .serializers import PostCreateSerializer, PostListSerializer
from django.utils import timezone
from .services import haversine_distance
from locations.models import Location
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .models import Post
from .serializers import PostCreateSerializer
# CUSTOMER: Create Post
def admin_only(user):
    return user.user_type == 'admin'

class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'customer':
            return Response(
                {"error": "Only customers can create posts"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PostCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        return Response(
            {"message": "Post created", "post_code": post.post_code},
            status=status.HTTP_201_CREATED
        )


# CUSTOMER: View Own Posts
class CustomerPostsView(APIView):
    def get(self, request):
        posts = Post.objects.filter(customer=request.user)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)


# DRIVER: View Available Posts
class DriverAvailablePostsView(APIView):
    def get(self, request):
        if request.user.user_type != 'driver':
            return Response(
                {"error": "Only drivers can view available posts"},
                status=status.HTTP_403_FORBIDDEN
            )

        vehicle = request.user.current_vehicle
        if not vehicle:
            return Response(
                {"error": "Driver has no vehicle assigned"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mandatory filters FIRST
        posts = Post.objects.filter(
            status='Posted',
            is_expired=False,
            vehicle_type=vehicle.vehicle_type,
            load_type=vehicle.load_type,
            required_date__gte=timezone.now()
        )

        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
class AdminAvailablePostsView(APIView):
    def get(self, request):
        if not admin_only(request.user):
            return Response(
                {"error": "Admin access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        posts = Post.objects.filter(
            status='Posted',
            is_expired=False
        )

        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
class AdminTakePostView(APIView):
    def post(self, request, post_id):
        if not admin_only(request.user):
            return Response(
                {"error": "Admin access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if post.status != 'Posted':
            return Response(
                {"error": "Post is not available"},
                status=status.HTTP_400_BAD_REQUEST
            )

        driver_id = request.data.get('driver_id')
        if not driver_id:
            return Response(
                {"error": "driver_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            driver = User.objects.get(
                id=driver_id,
                user_type='driver',
                status='active'
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid driver"},
                status=status.HTTP_400_BAD_REQUEST
            )

        post.status = 'Taken'
        post.driver = driver
        post.assigned_admin = request.user
        post.save()

        return Response({"message": "Post taken successfully"})
class AdminTakenPostsView(APIView):
    def get(self, request):
        if not admin_only(request.user):
            return Response(
                {"error": "Admin access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        posts = Post.objects.filter(status='Taken')
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
class AdminFinishPostView(APIView):
    def post(self, request, post_id):
        if not admin_only(request.user):
            return Response(
                {"error": "Admin access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if post.status != 'Taken':
            return Response(
                {"error": "Post is not in taken state"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if post.assigned_admin != request.user:
            return Response(
                {"error": "You are not assigned to this post"},
                status=status.HTTP_403_FORBIDDEN
            )

        post.status = 'Finished'
        post.save()

        return Response({"message": "Post finished successfully"})
class AdminReleasePostView(APIView):
    def post(self, request, post_id):
        if not admin_only(request.user):
            return Response(
                {"error": "Admin access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if post.status != 'Taken':
            return Response(
                {"error": "Post is not taken"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if post.assigned_admin != request.user:
            return Response(
                {"error": "You are not assigned to this post"},
                status=status.HTTP_403_FORBIDDEN
            )

        post.status = 'Posted'
        post.driver = None
        post.assigned_admin = None
        post.save()

        return Response({"message": "Post released back to available"})


class DriverAvailablePostsView(APIView):
    def get(self, request):
        if request.user.user_type != 'driver':
            return Response(
                {"error": "Driver access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        driver = request.user

        if not driver.current_vehicle:
            return Response(
                {"error": "Driver has no assigned vehicle"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if driver.current_latitude is None or driver.current_longitude is None:
            return Response(
                {"error": "Driver location not set"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optional filters
        pickup_id = request.GET.get('pickup_location')
        dropoff_id = request.GET.get('dropoff_location')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        posts = Post.objects.filter(
            status='Posted',
            is_expired=False,
            vehicle_type=driver.current_vehicle.vehicle_type,
            load_type=driver.current_vehicle.load_type,
            required_date__gte=timezone.now()
        ).select_related('pickup_location', 'dropoff_location')

        if pickup_id:
            posts = posts.filter(pickup_location_id=pickup_id)

        if dropoff_id:
            posts = posts.filter(dropoff_location_id=dropoff_id)

        if date_from and date_to:
            posts = posts.filter(required_date__date__range=[date_from, date_to])

        results = []

        for post in posts:
            distance = haversine_distance(
                driver.current_latitude,
                driver.current_longitude,
                post.pickup_location.latitude,
                post.pickup_location.longitude
            )

            results.append({
                "id": post.id,
                "post_code": post.post_code,
                "pickup": post.pickup_location.name,
                "dropoff": post.dropoff_location.name,
                "required_date": post.required_date,
                "distance_km": distance
            })

        results.sort(key=lambda x: x['distance_km'])
        return Response(results)

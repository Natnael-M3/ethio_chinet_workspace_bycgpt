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
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Post
# from .serializers import AdminCreateCustomerPostSerializer
# posts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .serializers import AdminPostForCustomerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from .models import Post, DriverRating
from .serializers import DriverRatingSerializer
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.models import User
from vehicles.models import Vehicle
from posts.models import Post

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

        # ✅ Admin only
        if not request.user.is_staff:
            return Response(
                {"error": "Admin access only"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ Get post
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Status check
        if post.status != 'posted':
            return Response(
                {"error": "Post is not available"},
                status=status.HTTP_400_BAD_REQUEST
            )

        phone_number = request.data.get('phone_number')
        plate_number = request.data.get('plate_number')

        # ❌ both provided
        if phone_number and plate_number:
            return Response(
                {"error": "Provide only phone_number OR plate_number, not both"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ❌ none provided
        if not phone_number and not plate_number:
            return Response(
                {"error": "phone_number or plate_number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        driver = None

        # ========================
        # OPTION 1 → phone_number
        # ========================
        if phone_number:
            try:
                driver = User.objects.get(
                    phone_number=phone_number,
                    user_type='driver',
                    status='active'
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "Driver with this phone number not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ========================
        # OPTION 2 → plate_number
        # ========================
        elif plate_number:
            try:
                vehicle = Vehicle.objects.select_related('driver').get(
                    plate_number=plate_number
                )
                driver = vehicle.driver

                if driver.user_type != 'driver' or driver.status != 'active':
                    return Response(
                        {"error": "Vehicle driver is not active"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except Vehicle.DoesNotExist:
                return Response(
                    {"error": "Vehicle with this plate number not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ✅ Assign post
        post.status = 'taken'
        post.driver = driver
        post.assigned_admin = request.user
        post.save()

        return Response(
            {
                "message": "Post taken successfully",
                "post_id": post.id,
                "driver_id": driver.id
            },
            status=status.HTTP_200_OK
        )


# class AdminTakePostView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, post_id):
#         if not admin_only(request.user):
#             return Response({"error": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)
#         try:
#             post = Post.objects.get(id=post_id)
#         except Post.DoesNotExist:
#             return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
#         if post.status != 'posted':
#             return Response({"error": "Post is not available"}, status=status.HTTP_400_BAD_REQUEST)

#         driver_id = request.data.get('driver_id')
#         try:
#             driver = User.objects.get(id=driver_id, user_type='driver', status='active')
#         except User.DoesNotExist:
#             return Response({"error": "Invalid driver"}, status=status.HTTP_400_BAD_REQUEST)

#         post.status = 'taken'
#         post.driver = driver
#         post.assigned_admin = request.user
#         post.save()
#         return Response({"message": "Post taken successfully"})

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
        post.status = 'finished'
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
            status="finished",
            driver=user,
        )

        serializer = DriverFinishedPostSerializer(posts, many=True)
        return Response(serializer.data)

class AdminPostCustomerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminPostForCustomerSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        return Response(
            {
                "message": "Post created successfully for customer",
                "post_id": post.id,
                "customer_id": post.customer.id,
                "customer_phone": post.customer.phone_number
            },
            status=status.HTTP_201_CREATED
        )


class UpdateDriverRatingView(APIView):
    """
    Admin can update/recalculate driver rating based on finished posts.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, driver_id):
        try:
            driver = User.objects.get(id=driver_id, user_type='driver')
        except User.DoesNotExist:
            return Response({"detail": "Driver not found."}, status=status.HTTP_404_NOT_FOUND)

        # Count total deliveries assigned to driver
        total_deliveries = Post.objects.filter(driver=driver).count()
        if total_deliveries == 0:
            success_rate = 0
        else:
            # Count successful deliveries
            successful_deliveries = Post.objects.filter(driver=driver, status='finished').count()
            success_rate = round((successful_deliveries / total_deliveries) * 5, 2)  # rating out of 5

        # Update or create driver rating
        rating_obj, created = DriverRating.objects.update_or_create(
            driver=driver,
            defaults={
                'success_rate': success_rate,
                'last_updated': timezone.now()
            }
        )

        serializer = DriverRatingSerializer(rating_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetDriverRatingView(APIView):
    """
    Anyone can fetch the current driver rating
    """
    def get(self, request, driver_id):
        try:
            driver = User.objects.get(id=driver_id, user_type='driver')
            rating_obj = DriverRating.objects.get(driver=driver)
        except User.DoesNotExist:
            return Response({"detail": "Driver not found."}, status=status.HTTP_404_NOT_FOUND)
        except DriverRating.DoesNotExist:
            return Response({"detail": "Rating not available yet."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DriverRatingSerializer(rating_obj)
        return Response(serializer.data)


class DriverSelfRatingView(APIView):
    """
    Logged-in driver can view their own rating
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'driver':
            return Response({"detail": "Access denied. Only drivers can view this."}, status=403)
        
        try:
            rating = DriverRating.objects.get(driver=request.user)
        except DriverRating.DoesNotExist:
            return Response({"detail": "Rating not available yet."}, status=404)
        
        return Response({
            "driver_id": request.user.id,
            "driver_name": request.user.get_full_name(),
            "rating": round(rating.success_rate, 2),
            "last_updated": rating.last_updated
        })

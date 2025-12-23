from django.urls import path
from .views import (
    CreatePostView,
    CustomerPostsView,
    DriverAvailablePostsView,
    AdminAvailablePostsView,
    AdminTakePostView,
    AdminTakenPostsView,
    AdminFinishPostView,
    AdminReleasePostView,
)

urlpatterns = [
    path('create/', CreatePostView.as_view()),
    path('my-posts/', CustomerPostsView.as_view()),
    path('available/', DriverAvailablePostsView.as_view()),
    path('admin/available/', AdminAvailablePostsView.as_view()),
    path('admin/take/<int:post_id>/', AdminTakePostView.as_view()),
    path('admin/taken/', AdminTakenPostsView.as_view()),
    path('admin/finish/<int:post_id>/', AdminFinishPostView.as_view()),
    path('admin/release/<int:post_id>/', AdminReleasePostView.as_view()),
]



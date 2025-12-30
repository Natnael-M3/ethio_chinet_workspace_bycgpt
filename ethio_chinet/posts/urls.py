from django.urls import path
from .views import (
    CreatePostView,
    CustomerPostsView,
    AdminAvailablePostsView,
    AdminTakePostView,
    AdminTakenPostsView,
    AdminFinishPostView,
    AdminReleasePostView,
    DriverAvailablePostsView,
    DriverTakenPostsView,
    DriverFinishedPostsView,
)

urlpatterns = [
    path('create/', CreatePostView.as_view()),
    path('my-posts/', CustomerPostsView.as_view()),
    path('admin/available/', AdminAvailablePostsView.as_view()),
    path('admin/take/<int:post_id>/', AdminTakePostView.as_view()),
    path('admin/taken/', AdminTakenPostsView.as_view()),
    path('admin/finish/<int:post_id>/', AdminFinishPostView.as_view()),
    path('admin/release/<int:post_id>/', AdminReleasePostView.as_view()),
    path("driver/available/", DriverAvailablePostsView.as_view()),
    path("driver/taken/", DriverTakenPostsView.as_view()),
    path("driver/finished/", DriverFinishedPostsView.as_view()),
]

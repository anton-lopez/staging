from django.urls import path
from . import views
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView, UserPostListView,
    PostImageDeleteView, DormListView, DormDetailView,
    DormCreateView, DormUpdateView, DormDeleteView,
    RoomListView, RoomDetailView, RoomCreateView,
    RoomUpdateView, RoomDeleteView, RoomImageDeleteView
)

urlpatterns = [
    path('', views.home, name='review-home'),  # Root path now points to the blank home page
    path('about/', views.about, name='review-about'),

    # Dorm URLs with slug - IMPORTANT: Create path must come BEFORE detail path
    path('dorms/', DormListView.as_view(), name='dorm-list'),
    path('dorm/new/', DormCreateView.as_view(), name='dorm-create'),  # Create must be before detail
    path('dorm/<slug:slug>/', DormDetailView.as_view(), name='dorm-detail'),
    path('dorm/<slug:slug>/update/', DormUpdateView.as_view(), name='dorm-update'),
    path('dorm/<slug:slug>/delete/', DormDeleteView.as_view(), name='dorm-delete'),
    path('dorm/<slug:dorm_slug>/room/new/', RoomCreateView.as_view(), name='dorm-room-create'),

    # Room URLs - legacy numeric ID routes (keep for backwards compatibility)
    path('rooms/', RoomListView.as_view(), name='room-list'),
    path('room/new/', RoomCreateView.as_view(), name='room-create'),
    path('room/<int:pk>/', views.room_redirect_view, name='room-detail-by-id'),
    path('room/<int:pk>/update/', views.room_update_redirect_view, name='room-update-redirect'),
    path('room/<int:pk>/delete/', views.room_delete_redirect_view, name='room-delete-redirect'),

    # Legacy URL for adding a room to a specific dorm using ID
    path('dorm/<int:dorm_id>/room/new/', views.dorm_room_create_redirect, name='legacy-dorm-room-create'),
    path('room/<int:room_id>/review/new/', views.room_review_create_redirect, name='legacy-room-review-create'),

    # New slug-based room URLs
    path('dorm/<slug:dorm_slug>/room/new/', RoomCreateView.as_view(), name='dorm-room-create'),
    path('dorm/<slug:dorm_slug>/<slug:room_slug>/', RoomDetailView.as_view(), name='room-detail'),
    path('dorm/<slug:dorm_slug>/<slug:room_slug>/update/', RoomUpdateView.as_view(), name='room-update'),
    path('dorm/<slug:dorm_slug>/<slug:room_slug>/delete/', RoomDeleteView.as_view(), name='room-delete'),
    path('room/image/<int:pk>/delete/', RoomImageDeleteView.as_view(), name='room-image-delete'),

    # Review URLs
    path('reviews/', PostListView.as_view(), name='review-list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('dorm/<slug:dorm_slug>/<slug:room_slug>/review/new/', PostCreateView.as_view(), name='room-review-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/image/<int:pk>/delete/', PostImageDeleteView.as_view(), name='post-image-delete'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
]

from django.urls import path
from . import views
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView, UserPostListView,
    PostImageDeleteView, DormListView, DormDetailView,
    DormCreateView, DormUpdateView, DormDeleteView,
    RoomListView, RoomDetailView, RoomCreateView,
    RoomUpdateView, RoomDeleteView
)

urlpatterns = [
    path('', views.home, name='review-home'),  # Root path now points to the blank home page
    path('about/', views.about, name='review-about'),

    # Dorm URLs
    path('dorms/', DormListView.as_view(), name='dorm-list'),
    path('dorm/<int:pk>/', DormDetailView.as_view(), name='dorm-detail'),
    path('dorm/new/', DormCreateView.as_view(), name='dorm-create'),
    path('dorm/<int:pk>/update/', DormUpdateView.as_view(), name='dorm-update'),
    path('dorm/<int:pk>/delete/', DormDeleteView.as_view(), name='dorm-delete'),

    # Room URLs
    path('rooms/', RoomListView.as_view(), name='room-list'),
    path('room/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    path('room/new/', RoomCreateView.as_view(), name='room-create'),
    path('dorm/<int:dorm_id>/room/new/', RoomCreateView.as_view(), name='dorm-room-create'),
    path('room/<int:pk>/update/', RoomUpdateView.as_view(), name='room-update'),
    path('room/<int:pk>/delete/', RoomDeleteView.as_view(), name='room-delete'),

    # Review URLs
    path('reviews/', PostListView.as_view(), name='review-list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('room/<int:room_id>/review/new/', PostCreateView.as_view(), name='room-review-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/image/<int:pk>/delete/', PostImageDeleteView.as_view(), name='post-image-delete'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
]
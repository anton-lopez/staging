from django.urls import path
from . import views
from .views import (PostListView, PostDetailView, PostCreateView,
                   PostUpdateView, PostDeleteView, UserPostListView,
                   PostImageDeleteView)

urlpatterns = [
    path('', PostListView.as_view(), name='review-home'),
    path('about/', views.about, name='review-about'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/image/<int:pk>/delete/', PostImageDeleteView.as_view(), name='post-image-delete'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
]
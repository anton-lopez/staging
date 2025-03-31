from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (ListView, DetailView, DeleteView)
from django.views import View
from .models import Post, PostImage
from .forms import PostForm, PostImageForm


class PostListView(ListView):
    model = Post
    template_name = 'review/home.html'
    context_object_name = 'reviews'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'review/user_posts.html'
    context_object_name = 'reviews'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, View):
    def get(self, request):
        post_form = PostForm()
        image_form = PostImageForm()
        return render(request, 'review/post_form.html', {
            'post_form': post_form,
            'image_form': image_form
        })

    def post(self, request):
        post_form = PostForm(request.POST)
        image_form = PostImageForm(request.POST, request.FILES)

        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()

            # Handle image uploads
            images = request.FILES.getlist('image')
            for img in images:
                # Create a new PostImage with an empty caption
                PostImage.objects.create(post=post, image=img, caption='')

            messages.success(request, 'Post created successfully!')
            return redirect('post-detail', pk=post.pk)

        return render(request, 'review/post_form.html', {
            'post_form': post_form,
            'image_form': image_form
        })


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post_form = PostForm(instance=post)
        image_form = PostImageForm()

        return render(request, 'review/post_update.html', {
            'post_form': post_form,
            'image_form': image_form,
            'post': post
        })

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post_form = PostForm(request.POST, instance=post)
        image_form = PostImageForm(request.POST, request.FILES)

        if post_form.is_valid():
            post = post_form.save()

            # Handle the file upload
            files = request.FILES.getlist('image')
            for f in files:
                # Create a new PostImage with an empty caption
                PostImage.objects.create(post=post, image=f, caption='')

            messages.success(request, 'Post updated successfully!')
            return redirect('post-detail', pk=post.pk)

        return render(request, 'review/post_update.html', {
            'post_form': post_form,
            'image_form': image_form,
            'post': post
        })

    def test_func(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/review/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        image = get_object_or_404(PostImage, pk=pk)
        post = image.post

        if request.user == post.author:
            image.delete()
            messages.success(request, 'Image deleted successfully!')

        return redirect('post-update', pk=post.pk)

    def test_func(self):
        image = get_object_or_404(PostImage, pk=self.kwargs.get('pk'))
        return self.request.user == image.post.author


def home(request):
    context = {
        'reviews': Post.objects.all(),
    }
    return render(request, 'review/home.html', context)


def about(request):
    return render(request, 'review/about.html', {'title': 'About'})
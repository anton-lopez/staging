from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (ListView, DetailView, DeleteView, CreateView, UpdateView)
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import Post, PostImage, Dorm, Room
from .forms import PostForm, PostImageForm, DormForm, RoomForm


class DormListView(ListView):
    model = Dorm
    template_name = 'review/dorm_list.html'
    context_object_name = 'dorms'
    ordering = ['name']


class DormDetailView(DetailView):
    model = Dorm
    template_name = 'review/dorm_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms = Room.objects.filter(dorm=self.object).order_by('room_number')
        rooms_with_stats = []

        for room in rooms:
            reviews = room.reviews.all()
            total_reviews = reviews.count()
            liked_reviews = sum(1 for review in reviews if review.liked)

            like_percentage = 0
            if total_reviews > 0:
                like_percentage = (liked_reviews / total_reviews) * 100

            rooms_with_stats.append({
                'room': room,
                'total_reviews': total_reviews,
                'liked_reviews': liked_reviews,
                'like_percentage': like_percentage
            })

        context['rooms_with_stats'] = rooms_with_stats
        return context


@method_decorator(staff_member_required, name='dispatch')
class DormCreateView(LoginRequiredMixin, CreateView):
    model = Dorm
    form_class = DormForm
    template_name = 'review/dorm_form.html'
    success_url = reverse_lazy('dorm-list')


@method_decorator(staff_member_required, name='dispatch')
class DormUpdateView(LoginRequiredMixin, UpdateView):
    model = Dorm
    form_class = DormForm
    template_name = 'review/dorm_form.html'

    def get_success_url(self):
        return reverse('dorm-detail', kwargs={'pk': self.object.pk})


@method_decorator(staff_member_required, name='dispatch')
class DormDeleteView(LoginRequiredMixin, DeleteView):
    model = Dorm
    template_name = 'review/dorm_confirm_delete.html'
    success_url = reverse_lazy('dorm-list')


class RoomListView(ListView):
    model = Room
    template_name = 'review/room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return Room.objects.all().order_by('dorm__name', 'room_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms_with_stats = []

        for room in context['rooms']:
            reviews = room.reviews.all()
            total_reviews = reviews.count()
            liked_reviews = sum(1 for review in reviews if review.liked)

            like_percentage = 0
            if total_reviews > 0:
                like_percentage = (liked_reviews / total_reviews) * 100

            rooms_with_stats.append({
                'room': room,
                'total_reviews': total_reviews,
                'liked_reviews': liked_reviews,
                'like_percentage': like_percentage
            })

        context['rooms_with_stats'] = rooms_with_stats
        return context


class RoomDetailView(DetailView):
    model = Room
    template_name = 'review/room_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Post.objects.filter(room=self.object).order_by('-date_posted')
        context['like_count'] = Post.objects.filter(room=self.object, liked=True).count()
        context['total_reviews'] = context['reviews'].count()
        if context['total_reviews'] > 0:
            context['like_percentage'] = (context['like_count'] / context['total_reviews']) * 100
        else:
            context['like_percentage'] = 0
        return context


@method_decorator(staff_member_required, name='dispatch')
class RoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'review/room_form.html'

    def get_success_url(self):
        return reverse('dorm-detail', kwargs={'pk': self.object.dorm.pk})

    def get_initial(self):
        initial = super().get_initial()
        if 'dorm_id' in self.kwargs:
            initial['dorm'] = get_object_or_404(Dorm, pk=self.kwargs['dorm_id'])
        return initial


@method_decorator(staff_member_required, name='dispatch')
class RoomUpdateView(LoginRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'review/room_form.html'

    def get_success_url(self):
        return reverse('room-detail', kwargs={'pk': self.object.pk})


@method_decorator(staff_member_required, name='dispatch')
class RoomDeleteView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = 'review/room_confirm_delete.html'

    def get_success_url(self):
        return reverse('dorm-detail', kwargs={'pk': self.object.dorm.pk})


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
    def get(self, request, room_id=None):
        # Check if user has an assigned room
        if not request.user.profile.assigned_room:
            messages.error(request, 'You must be assigned to a room in your profile before you can post a review.')
            return redirect('profile')

        # Pre-select the room based on user's profile
        post_form = PostForm(initial={'room': request.user.profile.assigned_room})
        image_form = PostImageForm()

        # Disable and mark as readonly the room field
        post_form.fields['room'].disabled = True
        post_form.fields['room'].widget.attrs.update({'readonly': True})
        # Remove the required attribute from the room field
        post_form.fields['room'].required = False

        return render(request, 'review/post_form.html', {
            'post_form': post_form,
            'image_form': image_form
        })

    def post(self, request, room_id=None):
        # Check if user has an assigned room
        if not request.user.profile.assigned_room:
            messages.error(request, 'You must be assigned to a room in your profile before you can post a review.')
            return redirect('profile')

        # Create a modified POST copy that we can change
        post_data = request.POST.copy()

        # Force-set the room value to the user's assigned room
        # This handles cases where the disabled field isn't submitted
        post_data['room'] = request.user.profile.assigned_room.id

        post_form = PostForm(post_data)
        image_form = PostImageForm(request.POST, request.FILES)

        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            # Always use the room from the profile
            post.room = request.user.profile.assigned_room
            post.save()

            # Handle image uploads
            images = request.FILES.getlist('image')
            for img in images:
                # Create a new PostImage with an empty caption
                PostImage.objects.create(post=post, image=img, caption='')

            messages.success(request, 'Review posted successfully!')
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

        # Disable the room field and mark as readonly
        post_form.fields['room'].disabled = True
        post_form.fields['room'].widget.attrs.update({'readonly': True})
        # Remove the required attribute from the room field
        post_form.fields['room'].required = False

        return render(request, 'review/post_update.html', {
            'post_form': post_form,
            'image_form': image_form,
            'post': post
        })

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        # Create a modified POST copy
        post_data = request.POST.copy()

        # Force-set the room value to the original post's room
        post_data['room'] = post.room.id

        post_form = PostForm(post_data, instance=post)
        image_form = PostImageForm(request.POST, request.FILES)

        if post_form.is_valid():
            updated_post = post_form.save(commit=False)
            # Ensure the room hasn't been changed
            updated_post.room = post.room
            updated_post.save()

            # Handle the file upload
            files = request.FILES.getlist('image')
            for f in files:
                # Create a new PostImage with an empty caption
                PostImage.objects.create(post=post, image=f, caption='')

            messages.success(request, 'Review updated successfully!')
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
        'dorms': Dorm.objects.all(),
    }
    return render(request, 'review/home.html', context)


def about(request):
    return render(request, 'review/about.html', {'title': 'About'})
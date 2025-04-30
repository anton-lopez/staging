from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (ListView, DetailView, DeleteView, CreateView, UpdateView)
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import Post, PostImage, Dorm, Room, RoomImage
from .forms import PostForm, PostImageForm, DormForm, RoomForm, RoomImageForm


def home(request):
    """View function for the blank home page"""
    return render(request, 'review/home.html', {'title': 'Home'})


def about(request):
    return render(request, 'review/about.html', {'title': 'About'})


# Redirect functions for backward compatibility with ID-based URLs
def room_redirect_view(request, pk):
    """Redirect old numeric ID URLs to new slug-based URLs"""
    room = get_object_or_404(Room, pk=pk)
    return redirect('room-detail', dorm_slug=room.dorm.slug, room_slug=room.slug)


def room_update_redirect_view(request, pk):
    """Redirect old numeric ID URLs for room updates to new slug-based URLs"""
    room = get_object_or_404(Room, pk=pk)
    return redirect('room-update', dorm_slug=room.dorm.slug, room_slug=room.slug)


def room_delete_redirect_view(request, pk):
    """Redirect old numeric ID URLs for room deletion to new slug-based URLs"""
    room = get_object_or_404(Room, pk=pk)
    return redirect('room-delete', dorm_slug=room.dorm.slug, room_slug=room.slug)


class DormListView(ListView):
    model = Dorm
    template_name = 'review/dorm_list.html'
    context_object_name = 'dorms'
    ordering = ['name']


class DormDetailView(DetailView):
    model = Dorm
    template_name = 'review/dorm_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

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
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        return reverse('dorm-detail', kwargs={'slug': self.object.slug})


@method_decorator(staff_member_required, name='dispatch')
class DormDeleteView(LoginRequiredMixin, DeleteView):
    model = Dorm
    template_name = 'review/dorm_confirm_delete.html'
    success_url = reverse_lazy('dorm-list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


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


# Add this to the RoomDetailView class in views.py if not already there
class RoomDetailView(DetailView):
    model = Room
    template_name = 'review/room_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'room_slug'

    def get_object(self):
        """Get room based on dorm slug and room slug"""
        dorm_slug = self.kwargs.get('dorm_slug')
        room_slug = self.kwargs.get('room_slug')
        dorm = get_object_or_404(Dorm, slug=dorm_slug)
        return get_object_or_404(Room, dorm=dorm, slug=room_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Post.objects.filter(room=self.object).order_by('-date_posted')
        context['like_count'] = Post.objects.filter(room=self.object, liked=True).count()
        context['total_reviews'] = context['reviews'].count()
        if context['total_reviews'] > 0:
            context['like_percentage'] = (context['like_count'] / context['total_reviews']) * 100
        else:
            context['like_percentage'] = 0

        # Make sure we're not sending the room ID for URL generation
        context['room_slug'] = self.object.slug
        context['dorm_slug'] = self.object.dorm.slug

        return context


@method_decorator(staff_member_required, name='dispatch')
class RoomCreateView(LoginRequiredMixin, View):
    def get(self, request, dorm_slug=None, dorm_id=None):
        initial = {}
        if dorm_slug:
            initial['dorm'] = get_object_or_404(Dorm, slug=dorm_slug)
        elif dorm_id:
            initial['dorm'] = get_object_or_404(Dorm, pk=dorm_id)

        form = RoomForm(initial=initial)
        image_form = RoomImageForm()

        return render(request, 'review/room_form.html', {
            'form': form,
            'image_form': image_form
        })

    def post(self, request, dorm_slug=None, dorm_id=None):
        initial = {}
        if dorm_slug:
            initial['dorm'] = get_object_or_404(Dorm, slug=dorm_slug)
        elif dorm_id:
            initial['dorm'] = get_object_or_404(Dorm, pk=dorm_id)

        form = RoomForm(request.POST, request.FILES, initial=initial)
        image_form = RoomImageForm(request.POST, request.FILES)

        # Check for duplicate room before full validation
        if 'dorm' in form.data and 'room_number' in form.data:
            try:
                dorm_id = int(form.data['dorm'])
                room_number = form.data['room_number']

                # Check if this room already exists in this dorm
                if Room.objects.filter(dorm_id=dorm_id, room_number=room_number).exists():
                    dorm = Dorm.objects.get(id=dorm_id)
                    form.add_error('room_number',
                                   f'Room {room_number} already exists in {dorm.name}. Please use a different room number.')
                    return render(request, 'review/room_form.html', {
                        'form': form,
                        'image_form': image_form
                    })
            except (ValueError, Dorm.DoesNotExist):
                # Will be caught by form validation
                pass

        if form.is_valid():
            room = form.save()

            # Handle additional images using the specific field name
            if 'additional_images' in request.FILES:
                additional_images = request.FILES.getlist('additional_images')
                for img in additional_images:
                    RoomImage.objects.create(room=room, image=img)

            messages.success(request, 'Room created successfully!')
            return redirect('room-detail', dorm_slug=room.dorm.slug, room_slug=room.slug)

        return render(request, 'review/room_form.html', {
            'form': form,
            'image_form': image_form
        })


@method_decorator(staff_member_required, name='dispatch')
class RoomUpdateView(LoginRequiredMixin, View):
    def get_object(self):
        """Get room based on dorm slug and room slug"""
        dorm_slug = self.kwargs.get('dorm_slug')
        room_slug = self.kwargs.get('room_slug')
        dorm = get_object_or_404(Dorm, slug=dorm_slug)
        return get_object_or_404(Room, dorm=dorm, slug=room_slug)

    def get(self, request, dorm_slug=None, room_slug=None, pk=None):
        if pk:
            # Handle legacy URLs (should be redirected before getting here)
            room = get_object_or_404(Room, pk=pk)
            return redirect('room-update', dorm_slug=room.dorm.slug, room_slug=room.slug)

        room = self.get_object()
        form = RoomForm(instance=room)
        image_form = RoomImageForm()

        return render(request, 'review/room_update.html', {
            'form': form,
            'image_form': image_form,
            'room': room
        })

    def post(self, request, dorm_slug=None, room_slug=None, pk=None):
        if pk:
            # Handle legacy URLs (should be redirected before getting here)
            room = get_object_or_404(Room, pk=pk)
            return redirect('room-update', dorm_slug=room.dorm.slug, room_slug=room.slug)

        room = self.get_object()
        form = RoomForm(request.POST, request.FILES, instance=room)
        image_form = RoomImageForm(request.POST, request.FILES)

        # Check for duplicate room before full validation
        if 'dorm' in form.data and 'room_number' in form.data:
            try:
                dorm_id = int(form.data['dorm'])
                room_number = form.data['room_number']

                # Check if this room already exists in this dorm (excluding the current room)
                if Room.objects.filter(dorm_id=dorm_id, room_number=room_number).exclude(pk=room.pk).exists():
                    dorm = Dorm.objects.get(id=dorm_id)
                    form.add_error('room_number',
                                   f'Room {room_number} already exists in {dorm.name}. Please use a different room number.')
                    return render(request, 'review/room_update.html', {
                        'form': form,
                        'image_form': image_form,
                        'room': room
                    })
            except (ValueError, Dorm.DoesNotExist):
                # Will be caught by form validation
                pass

        if form.is_valid():
            updated_room = form.save()

            # Handle additional images using the specific field name
            if 'additional_images' in request.FILES:
                additional_images = request.FILES.getlist('additional_images')
                for img in additional_images:
                    RoomImage.objects.create(room=updated_room, image=img)

            messages.success(request, 'Room updated successfully!')
            return redirect('room-detail', dorm_slug=updated_room.dorm.slug, room_slug=updated_room.slug)

        return render(request, 'review/room_update.html', {
            'form': form,
            'image_form': image_form,
            'room': room
        })


@method_decorator(staff_member_required, name='dispatch')
class RoomDeleteView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = 'review/room_confirm_delete.html'

    def get_object(self):
        """Get room based on dorm slug and room slug"""
        dorm_slug = self.kwargs.get('dorm_slug')
        room_slug = self.kwargs.get('room_slug')
        dorm = get_object_or_404(Dorm, slug=dorm_slug)
        return get_object_or_404(Room, dorm=dorm, slug=room_slug)

    def get_success_url(self):
        return reverse('dorm-detail', kwargs={'slug': self.object.dorm.slug})


class PostListView(ListView):
    model = Post
    template_name = 'review/review_list.html'
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
    def get(self, request, room_id=None, dorm_slug=None, room_slug=None):
        # Check if user has an assigned room
        if not request.user.profile.assigned_room:
            messages.error(request, 'You must be assigned to a room in your profile before you can post a review.')
            return redirect('profile')

        # Pre-select the room based on user's profile or selected room
        if dorm_slug and room_slug:
            dorm = get_object_or_404(Dorm, slug=dorm_slug)
            room = get_object_or_404(Room, dorm=dorm, slug=room_slug)
            post_form = PostForm(initial={'room': room})
        elif room_id:
            room = get_object_or_404(Room, pk=room_id)
            post_form = PostForm(initial={'room': room})
        else:
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

    def post(self, request, room_id=None, dorm_slug=None, room_slug=None):
        # Check if user has an assigned room
        if not request.user.profile.assigned_room:
            messages.error(request, 'You must be assigned to a room in your profile before you can post a review.')
            return redirect('profile')

        # Create a modified POST copy that we can change
        post_data = request.POST.copy()

        # Determine which room to use
        if dorm_slug and room_slug:
            dorm = get_object_or_404(Dorm, slug=dorm_slug)
            room = get_object_or_404(Room, dorm=dorm, slug=room_slug)
            post_data['room'] = room.id
        elif room_id:
            room = get_object_or_404(Room, pk=room_id)
            post_data['room'] = room.id
        else:
            # Force-set the room value to the user's assigned room
            post_data['room'] = request.user.profile.assigned_room.id

        post_form = PostForm(post_data)
        image_form = PostImageForm(request.POST, request.FILES)

        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            # Use the determined room
            if dorm_slug and room_slug:
                dorm = get_object_or_404(Dorm, slug=dorm_slug)
                post.room = get_object_or_404(Room, dorm=dorm, slug=room_slug)
            elif room_id:
                post.room = get_object_or_404(Room, pk=room_id)
            else:
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
    success_url = '/reviews/'

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


@method_decorator(staff_member_required, name='dispatch')
class RoomImageDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        image = get_object_or_404(RoomImage, pk=pk)
        room = image.room

        image.delete()
        messages.success(request, 'Image deleted successfully!')

        return redirect('room-update', dorm_slug=room.dorm.slug, room_slug=room.slug)


def dorm_room_create_redirect(request, dorm_id):
    """Redirect from legacy room creation URL to new slug-based URL"""
    dorm = get_object_or_404(Dorm, pk=dorm_id)
    return redirect('dorm-room-create', dorm_slug=dorm.slug)


def room_review_create_redirect(request, room_id):
    """Redirect from legacy room review creation URL to new slug-based URL"""
    room = get_object_or_404(Room, pk=room_id)
    return redirect('room-review-create', dorm_slug=room.dorm.slug, room_slug=room.slug)

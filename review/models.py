from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
import os


class Dorm(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='dorm_images', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dorm-detail', kwargs={'pk': self.pk})


class Room(models.Model):
    dorm = models.ForeignKey(Dorm, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='room_images', blank=True, null=True)

    class Meta:
        unique_together = ['dorm', 'room_number']  # Ensure room numbers are unique within a dorm

    def __str__(self):
        return f"{self.dorm.name} - Room {self.room_number}"

    def get_absolute_url(self):
        return reverse('room-detail', kwargs={'pk': self.pk})


class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='room_gallery')
    caption = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.room.dorm.name} - Room {self.room.room_number} - Image"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Create a thumbnail
        if self.image:
            img = Image.open(self.image.path)
            img.thumbnail((800, 600), Image.LANCZOS)
            img.save(self.image.path, quality=85, optimize=True)


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews', null=True)
    liked = models.BooleanField(default=False)  # Added like feature

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images')
    caption = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.post.title} - Image"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Create a smaller rectangular thumbnail
        if self.image:
            # Open original image
            img = Image.open(self.image.path)

            # Resize to a small rectangle (keeping aspect ratio)
            img.thumbnail((300, 200), Image.LANCZOS)

            # Save back to the same file
            img.save(self.image.path, quality=85, optimize=True)

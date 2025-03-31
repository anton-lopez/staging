from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
import os


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images')
    caption = models.CharField(max_length=100, blank=True, null=True)  # Add null=True

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
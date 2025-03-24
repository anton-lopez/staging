from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=100)                        # title has a char limit of 100 characters
    content = models.TextField()                                    # Content currently has no character limit
    date_posted = models.DateTimeField(default=timezone.now)        # Sets the date posted to the users timezone
    author = models.ForeignKey(User, on_delete=models.CASCADE)      # If a user is deleted, delete their posts

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
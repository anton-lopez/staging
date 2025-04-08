from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from review.models import Room, Dorm


class RoomAssignmentLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    previous_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='previous_assignments')
    new_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_assignments')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} room change on {self.timestamp.strftime("%Y-%m-%d %H:%M")}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    assigned_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='assigned_students')

    def __str__(self):
        return f'{self.user.username} Profile'

    # Makes it so images are saved smaller
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    @property
    def assigned_dorm(self):
        if self.assigned_room:
            return self.assigned_room.dorm
        return None

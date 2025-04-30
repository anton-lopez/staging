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

    # Track the previous room for logging
    _original_assigned_room = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store the original room when instance is loaded
        self._original_assigned_room = self.assigned_room

    def __str__(self):
        return f'{self.user.username} Profile'

    # Makes it so images are saved smaller
    def save(self, *args, **kwargs):
        # Check if this is an existing instance and if room has changed
        if self.pk and self.assigned_room != self._original_assigned_room:
            # Create log entry for room change
            RoomAssignmentLog.objects.create(
                user=self.user,
                previous_room=self._original_assigned_room,
                new_room=self.assigned_room
            )

        super().save(*args, **kwargs)

        # After saving, update the original room to the current one
        self._original_assigned_room = self.assigned_room

        # Process profile image
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
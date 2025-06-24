from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from wagtail.images.models import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"
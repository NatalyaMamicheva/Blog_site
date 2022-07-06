from datetime import datetime

import pytz
from django.db import models
from django.contrib.auth.models import AbstractUser

from mainapp.mixins import ModelClassNameMixin


class User(AbstractUser, ModelClassNameMixin):
    user_about = models.CharField(max_length=1024, blank=True)
    avatar_link = models.ImageField(upload_to='users_images', blank=True)
    blocked_time = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(blank=True, unique=True)
    likes = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='user_likes')

    @property
    def is_banned(self):
        if self.blocked_time is not None:
            now = pytz.utc.localize(datetime.now())
            block_duration = now - self.blocked_time
            if block_duration.days < 14:
                return True
            else:
                self.blocked_time = None
                self.save()
                return False
        else:
            return False

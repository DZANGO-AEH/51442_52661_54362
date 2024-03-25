from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    is_content_creator = models.BooleanField(default=False, verbose_name="Content creator")
    def __str__(self):
        return self.username

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    is_content_creator = models.BooleanField(default=False, verbose_name="Are you a content creator?")
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to='avatars/', null=True, blank=True)
    background_pic = models.ImageField(upload_to='backgrounds/', null=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    website_url = models.URLField(_("Website URL"), max_length=255, null=True, blank=True)
    twitter_url = models.URLField(_("Twitter URL"), max_length=255, null=True, blank=True)
    instagram_url = models.URLField(_("Instagram URL"), max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Automatically create or update the user profile
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
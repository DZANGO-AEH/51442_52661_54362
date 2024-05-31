from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from .validators import validate_twitter_url, validate_instagram_url


class CustomUser(AbstractUser):
    """
    Model representing a custom user, extending Django's default user model (AbstractUser).

    Fields:
        - is_content_creator (BooleanField): Indicates whether the user is a content creator. Defaults to False
        - stripe_account_id (CharField): Stripe account ID associated with the user. Can be blank or null.
    """
    is_content_creator = models.BooleanField(default=False, verbose_name="Are you a content creator?")
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    Model representing a user profile, associated one-to-one with the custom user (CustomUser).

    Fields:
        - user (OneToOneField): The user to whom this profile belongs. Deletes the profile if the user is deleted.
        - profile_pic (ImageField): Profile picture of the user. Can be blank or null.
        - background_pic (ImageField): Background picture of the user's profile. Can be blank or null.
        - description (TextField): A brief description of the user. Can be blank.
        - website_url (URLField): URL of the user's website. Can be blank or null.
        - twitter_url (URLField): URL of the user's Twitter profile. Validated by `validate_twitter_url`. Can be blank or null.
        - instagram_url (URLField): URL of the user's Instagram profile. Validated by `validate_instagram_url`. Can be blank or null.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to='avatars/', null=True, blank=True)
    background_pic = models.ImageField(upload_to='backgrounds/', null=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    website_url = models.URLField(_("Website URL"), max_length=255, null=True, blank=True)
    twitter_url = models.URLField(_("Twitter URL"), max_length=255, null=True, blank=True,
                                  validators=[validate_twitter_url])
    instagram_url = models.URLField(_("Instagram URL"), max_length=255, null=True, blank=True,
                                    validators=[validate_instagram_url])

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates or updates a UserProfile whenever a CustomUser is created or updated.

    Args:
        sender (class): The model class sending the signal.
        instance (CustomUser): The actual instance being saved.
        created (bool): Whether this instance is being created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()


class Event(models.Model):
    """
    Model representing an event associated with a user.

    Fields:
        - user (ForeignKey): The user who triggered the event. Deletes events if the user is deleted.
        - event_type (CharField): Type of the event.
        - description (TextField): Description of the event.
        - timestamp (DateTimeField): Time when the event occurred. Automatically set to the current time when created.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.event_type} at {self.timestamp}'

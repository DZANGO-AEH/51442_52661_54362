from django.db import models
from account.models import CustomUser
from django.core.exceptions import ValidationError
from .helpers import get_upload_to
import mimetypes
from django.conf import settings


class Tier(models.Model):
    """
    Model representing a subscription tier.

    Attributes:
    - name: The name of the tier.
    - points_price: The price in points for subscribing to the tier.
    - description: A description of the tier.
    - user: The user who created the tier.
    - message_permission: Boolean indicating if the tier includes messaging permissions.
    """

    name = models.CharField(max_length=50)
    points_price = models.IntegerField()
    description = models.TextField(max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tiers')
    message_permission = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_tier_name_per_user')
        ]

    def __str__(self):
        return f'{self.name} - {self.points_price} points'


class Post(models.Model):
    """
    Model representing a post made by a user.

    Attributes:
    - title: The title of the post.
    - text: The content of the post.
    - posted_at: The date and time the post was made.
    - is_free: Boolean indicating if the post is free.
    - tier: The tier associated with the post.
    - user: The user who created the post.
    """

    title = models.CharField(max_length=100)
    text = models.TextField(max_length=1500)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_free = models.BooleanField(default=False, verbose_name="Is this a free post?")
    tier = models.ForeignKey(Tier, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_posts')

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        """
        Returns the number of likes for the post.
        """
        return self.likes.count()

    @property
    def comments_count(self):
        """
        Returns the number of comments on the post.
        """
        return self.comments.count()


class Media(models.Model):
    """
    Model representing media files associated with posts.

    Attributes:
    - post: The post to which the media file is attached.
    - file: The media file itself.
    - type: The type of media (image or video).
    - tier: The tier associated with the media file.
    """

    post = models.ForeignKey(Post, related_name='media', on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to=get_upload_to)
    type = models.CharField(max_length=10, editable=False)
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, editable=False, null=True)

    def save(self, *args, **kwargs):
        """
        Override the save method to determine the type of media and assign the tier.
        """
        if not self.id:
            mime_type, _ = mimetypes.guess_type(self.file.name)
            if mime_type:
                if mime_type.startswith('image'):
                    self.type = 'image'
                elif mime_type.startswith('video'):
                    self.type = 'video'
                else:
                    raise ValidationError("Unsupported file type.")
            self.tier = self.post.tier
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file.name

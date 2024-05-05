from django.db import models
from account.models import CustomUser as User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .helpers import get_upload_to
import stripe
import mimetypes
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY


class Tier(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tiers')
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    message_permission = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - ${self.price}'

    def save(self, *args, **kwargs):
        # Create or update the Stripe product
        if not self.stripe_product_id:
            product = stripe.Product.create(name=self.name, description=self.description)
            self.stripe_product_id = product.id
        else:
            product = stripe.Product.modify(self.stripe_product_id, name=self.name, description=self.description)

        # Create or update the Stripe price
        if not self.stripe_price_id:
            price = stripe.Price.create(
                unit_amount=int(self.price * 100),  # amount in cents
                currency="usd",
                recurring={"interval": "month"},
                product=self.stripe_product_id,
            )
            self.stripe_price_id = price.id
        else:
            # Stripe does not support price modification directly.
            # We must create a new price and disable the old one.
            old_price_id = self.stripe_price_id
            price = stripe.Price.create(
                unit_amount=int(self.price * 100),
                currency="usd",
                recurring={"interval": "month"},
                product=self.stripe_product_id,
            )
            self.stripe_price_id = price.id
            stripe.Price.modify(old_price_id, active=False)

        super().save(*args, **kwargs)


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, related_name='subscribers')
    stripe_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'tier'], condition=models.Q(status='ACTIVE'), name='unique_active_subscription_to_tier')
        ]

    def __str__(self):
        return f'{self.user.username} - {self.tier.name} subscription'

    def is_expired(self):
        return self.end_date < timezone.now()

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after the start date.")
        if self.end_date <= timezone.now():
            raise ValidationError("End date must be in the future.")

        # Validate that a user does not have multiple active subscriptions to the same creator
        if self.status == 'ACTIVE':
            # Check for other active subscriptions to the same creator
            other_active_subscriptions = Subscription.objects.filter(
                user=self.user,
                tier__user=self.tier.user,
                status='ACTIVE'
            ).exclude(id=self.id)

            if other_active_subscriptions.exists():
                raise ValidationError("You already have an active subscription with this creator.")


class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=1500)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_free = models.BooleanField(default=False, verbose_name="Is this a free post?")
    tier = models.ForeignKey(Tier, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def favourites_count(self):
        return self.favourites.count()


class Media(models.Model):
    post = models.ForeignKey(Post, related_name='media', on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to=get_upload_to)
    type = models.CharField(max_length=10, editable=False)  # No longer manually set
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, editable=False, null=True)  # Automatically use the post's tier

    def save(self, *args, **kwargs):
        if not self.id:  # only set the type and tier on initial save
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

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favourites')
    favourited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

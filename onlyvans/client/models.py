from django.db import models
from account.models import CustomUser
from creator.models import Tier
from django.core.exceptions import ValidationError
from django.utils import timezone

class Subscription(models.Model):
    """
    Model representing a subscription to a content creator's tier.
    """

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
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
        """
        Checks if the subscription is expired based on the end date.

        Returns:
            bool: True if the subscription is expired, False otherwise.
        """
        return self.end_date < timezone.now()

    def clean(self):
        """
        Custom validation for the Subscription model.

        Raises:
            ValidationError: If end date is not after the start date, if end date is in the past,
                             or if there is already an active subscription for the same creator.
        """
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after the start date.")
        if self.end_date <= timezone.now():
            raise ValidationError("End date must be in the future.")

        if self.status == 'ACTIVE':
            other_active_subscriptions = Subscription.objects.filter(
                user=self.user,
                tier__user=self.tier.user,
                status='ACTIVE'
            ).exclude(id=self.id)

            if other_active_subscriptions.exists():
                raise ValidationError("You already have an active subscription with this creator.")

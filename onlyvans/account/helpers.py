from django.db.models import Count
from django.utils import timezone
from creator.models import Tier, Post, Favourite, Subscription
from interactions.models import Like
from .models import Event
from .forms import UserPasswordChangeForm, CustomUserUpdateForm, UserProfileForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

def get_active_subscribers_count(user):
    """
    Get the total number of active subscribers for a given user.

    Args:
        user (CustomUser): The user whose active subscribers are being counted.

    Returns:
        int: The total number of active subscribers across all tiers of the user.
    """
    return sum(tier.subscribers.filter(status='ACTIVE').count() for tier in user.tiers.all())


def get_total_likes(user):
    """
    Get the total number of likes on all posts created by a given user.

    Args:
        user (CustomUser): The user whose posts' likes are being counted.

    Returns:
        int: The total number of likes across all posts by the user.
    """
    total_likes = Post.objects.filter(user=user).aggregate(total_likes=Count('likes'))['total_likes'] or 0
    return total_likes


def get_total_likes_given(user):
    """
    Get the total number of likes given by a given user.

    Args:
        user (CustomUser): The user whose given likes are being counted.

    Returns:
        int: The total number of likes given by the user.
    """
    return Like.objects.filter(user=user).count()


def get_total_subscriptions(user):
    """
    Get the total number of active subscriptions for a given user.

    Args:
        user (CustomUser): The user whose subscriptions are being counted.

    Returns:
        int: The total number of active subscriptions for the user.
    """
    return Subscription.objects.filter(user=user, end_date__gte=timezone.now(), status='ACTIVE').count()

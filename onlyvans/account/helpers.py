from django.db.models import Count, Q, Sum
from django.utils import timezone
from creator.models import Tier, Post, Favourite
import re
from django.core.exceptions import ValidationError

def get_active_subscribers_count(user):
    return sum(tier.subscribers.count() for tier in user.tiers.all())


def get_total_likes(user):
    # Aggregate likes across all posts by the user
    total_likes = Post.objects.filter(user=user).aggregate(
        total_likes=Sum('likes__id')  # Assumes each Like object has an auto-generated `id`
    )['total_likes']

    return total_likes or 0  # Return 0 if no likes are found

def get_total_favourites(user):
    total_favorites = Favourite.objects.filter(user=user).count()
    return total_favorites

def get_total_subscriptions(user):
    return user.subscriptions.filter(end_date__gte=timezone.now()).count()
from django.db.models import Count, Q, Sum
from django.utils import timezone
from creator.models import Tier, Post, Favourite, Subscription
import re
from django.core.exceptions import ValidationError

def get_active_subscribers_count(user):
    return sum(tier.subscribers.filter(status='ACTIVE').count() for tier in user.tiers.all())

def get_total_likes(user):
    total_likes = Post.objects.filter(user=user).aggregate(
        total_likes=Sum('likes__id')
    )['total_likes'] or 0
    return total_likes

def get_total_favourites(user):
    return Favourite.objects.filter(user=user).count()

def get_total_subscriptions(user):
    return Subscription.objects.filter(user=user, end_date__gte=timezone.now(), status='ACTIVE').count()
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from account.models import CustomUser as User
from creator.models import Tier, Subscription, Post
from django.db.models import Q, Value, CharField, Count
from .decorators import client_required
import random
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


@login_required(login_url='login')
@client_required
def dashboard(request):
    user = request.user

    # Get all active subscriptions
    active_subscriptions = Subscription.objects.filter(user=user, status='ACTIVE')

    # Get all content creators that the user is subscribed to
    followed_creators = [sub.tier.user for sub in active_subscriptions]

    # Fetch posts from the user's active subscriptions and free posts from followed content creators
    posts = Post.objects.filter(
        Q(user__in=followed_creators, is_free=True) |
        Q(user__in=followed_creators, tier__in=[sub.tier for sub in active_subscriptions])
    ).distinct().order_by('-posted_at')

    posts = posts.annotate(
        visible=Value(True, output_field=CharField())
    )
    return render(request, 'client/dashboard.html', {
        'posts': posts,
    })

@login_required(login_url='login')
@client_required
def discover_creators(request):
    search_query = request.GET.get('q', '')

    top_creators = User.objects.filter(is_content_creator=True).annotate(
        subscribers_count=Count(
            'tiers__subscribers',
            filter=Q(tiers__subscribers__status='ACTIVE')
        )
    ).order_by('-subscribers_count')[:6]

    new_faces = User.objects.filter(is_content_creator=True).annotate(
        subscribers_count=Count(
            'tiers__subscribers',
            filter=Q(tiers__subscribers__status='ACTIVE')
        )
    ).order_by('-date_joined')[:6]

    most_active_creators = User.objects.filter(is_content_creator=True).annotate(
        posts_count=Count('user_posts'),
        messages_count=Count('sent_messages')
    ).order_by('-posts_count', '-messages_count')[:6]

    all_creators = list(User.objects.filter(is_content_creator=True))
    random.shuffle(all_creators)
    random_creators = all_creators[:6]

    search_results = User.objects.filter(
        username__icontains=search_query, is_content_creator=True
    ).annotate(
        subscribers_count=Count(
            'tiers__subscribers',
            filter=Q(tiers__subscribers__status='ACTIVE')
        )
    ) if search_query else []

    return render(request, 'client/discover_creators.html', {
        'top_creators': top_creators,
        'new_faces': new_faces,
        'most_active_creators': most_active_creators,
        'random_creators': random_creators,
        'search_results': search_results,
        'search_query': search_query
    })
@login_required(login_url='login')
@client_required
def select_tier(request, username):
    creator = get_object_or_404(User, username=username, is_content_creator=True)
    tiers = Tier.objects.filter(user=creator)
    return render(request, 'client/select_tier.html', {'creator': creator, 'tiers': tiers})


@login_required(login_url='login')
@client_required
def subscribe_to_tier(request, username, tier_id):
    creator = get_object_or_404(User, username=username, is_content_creator=True)
    tier = get_object_or_404(Tier, id=tier_id, user=creator)
    user = request.user

    # Sprawdzenie, czy użytkownik ma już aktywną subskrypcję do tego twórcy
    active_subscription = Subscription.objects.filter(
        user=user,
        tier__user=creator,
        status='ACTIVE'
    ).exists()

    if active_subscription:
        messages.error(request, 'You already have an active subscription to this creator.')
        return redirect('client:dashboard')

    if user.wallet.balance < tier.points_price:
        messages.error(request, 'You do not have enough points to subscribe to this tier.')
        return redirect('client:select_tier', username=username)

    # Deduct points from user's wallet
    user.wallet.balance -= tier.points_price
    user.wallet.save()

    # Add points to creator's wallet
    creator.wallet.balance += tier.points_price
    creator.wallet.save()

    # Create subscription
    now = timezone.now()
    Subscription.objects.create(
        user=user,
        tier=tier,
        status='ACTIVE',
        start_date=now,
        end_date=now + timezone.timedelta(days=30)
    )

    messages.success(request, 'You have successfully subscribed to the tier.')
    return redirect('client:dashboard')



@login_required(login_url='login')
@client_required
def subscriptions(request):
    user = request.user
    subscriptions = Subscription.objects.filter(user=user, status='ACTIVE').select_related('tier__user')

    return render(request, 'client/subscriptions.html', {
        'subscriptions': subscriptions,
    })

@login_required(login_url='login')
@client_required
def extend_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user, status='ACTIVE')
    user = request.user
    tier = subscription.tier

    if user.wallet.balance < tier.points_price:
        messages.error(request, 'You do not have enough points to extend this subscription.')
        return redirect('client:subscriptions')

    # Deduct points from user's wallet
    user.wallet.balance -= tier.points_price
    user.wallet.save()

    # Add points to creator's wallet
    creator = tier.user
    creator.wallet.balance += tier.points_price
    creator.wallet.save()

    # Extend the subscription
    subscription.end_date += timezone.timedelta(days=30)
    subscription.save()

    messages.success(request, 'You have successfully extended the subscription.')
    return redirect('client:subscriptions')

@login_required(login_url='login')
@client_required
def cancel_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user, status='ACTIVE')
    subscription.status = 'CANCELLED'
    subscription.save()

    messages.success(request, 'You have successfully cancelled the subscription.')
    return redirect('client:subscriptions')
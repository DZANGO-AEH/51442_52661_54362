from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from account.models import CustomUser as User, Event
from creator.models import Tier, Post
from .models import Subscription
from interactions.models import Like
from finances.models import Wallet
from django.db.models import Q, Value, CharField, Count
from .decorators import client_required
import random
from django.core.paginator import Paginator
from django.utils import timezone


@login_required(login_url='login')
@client_required
def dashboard(request):
    """
    Display the client's dashboard with posts from followed creators.

    Retrieves active subscriptions of the user, followed creators, and their posts,
    then paginates the posts and returns the dashboard view.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered dashboard HTML page with posts and liked posts.
    """
    user = request.user
    active_subscriptions = Subscription.objects.filter(user=user, status='ACTIVE')
    followed_creators = [sub.tier.user for sub in active_subscriptions]
    posts_list = Post.objects.filter(
        Q(user__in=followed_creators, is_free=True) |
        Q(user__in=followed_creators, tier__in=[sub.tier for sub in active_subscriptions])
    ).distinct().order_by('-posted_at')

    posts_list = posts_list.annotate(visible=Value(True, output_field=CharField()))
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    liked_posts = Like.objects.filter(user=request.user, post__in=posts_list).values_list('post_id', flat=True)

    return render(request, 'client/dashboard.html', {
        'posts': posts,
        'liked_posts': liked_posts,
    })


@login_required(login_url='login')
@client_required
def discover_creators(request):
    """
    Display the discover creators page with various categories of creators.

    Fetches and displays top, new, most active, and random creators. Also handles search functionality.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered discover creators HTML page with categorized creators and search results.
    """
    search_query = request.GET.get('q', '')
    top_creators = User.objects.filter(is_content_creator=True).annotate(
        subscribers_count=Count('tiers__subscribers', filter=Q(tiers__subscribers__status='ACTIVE'))
    ).order_by('-subscribers_count')[:6]

    new_faces = User.objects.filter(is_content_creator=True).annotate(
        subscribers_count=Count('tiers__subscribers', filter=Q(tiers__subscribers__status='ACTIVE'))
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
        subscribers_count=Count('tiers__subscribers', filter=Q(tiers__subscribers__status='ACTIVE'))
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
    """
    Display the select tier page for a specific creator.

    Fetches the creator and their tiers, then returns the select tier view.

    Args:
        request: The HTTP request object.
        username: The username of the creator.

    Returns:
        Rendered select tier HTML page with the creator and their tiers.
    """
    creator = get_object_or_404(User, username=username, is_content_creator=True)
    tiers = Tier.objects.filter(user=creator)
    return render(request, 'client/select_tier.html', {'creator': creator, 'tiers': tiers})


@login_required(login_url='login')
@client_required
def subscribe_to_tier(request, username, tier_id):
    """
    Subscribe the user to a specific tier of a creator.

    Checks for an active subscription, verifies user wallet balance, deducts points,
    and creates the subscription. If the user or creator doesn't have a wallet, it creates one.

    Args:
        request: The HTTP request object.
        username: The username of the creator.
        tier_id: The ID of the tier to subscribe to.

    Returns:
        Redirects to the dashboard or select tier page with a success or error message.
    """
    creator = get_object_or_404(User, username=username, is_content_creator=True)
    tier = get_object_or_404(Tier, id=tier_id, user=creator)
    user = request.user

    if not hasattr(user, 'wallet'):
        Wallet.objects.create(user=user)

    if not hasattr(creator, 'wallet'):
        Wallet.objects.create(user=creator)

    active_subscription = Subscription.objects.filter(
        user=user,
        tier__user=creator,
        status='ACTIVE'
    ).exists()

    if active_subscription:
        messages.error(request, 'You already have an active subscription to this creator.')
        return redirect('client:subscriptions')

    if user.wallet.balance < tier.points_price:
        messages.error(request, 'You do not have enough points to subscribe to this tier.')
        return redirect('client:select-tier', username=username)

    user.wallet.balance -= tier.points_price
    user.wallet.save()
    creator.wallet.balance += tier.points_price
    creator.wallet.save()

    now = timezone.now()
    Subscription.objects.create(
        user=user,
        tier=tier,
        status='ACTIVE',
        start_date=now,
        end_date=now + timezone.timedelta(days=30)
    )

    Event.objects.create(
        user=user,
        event_type='SUBSCRIPTION',
        description=f'Subscribed to {creator.username}\'s {tier.name} tier for 30 days.'
    )

    Event.objects.create(
        user=creator,
        event_type='SUBSCRIPTION',
        description=f'{user.username} subscribed to your {tier.name} tier for 30 days.'
    )

    messages.success(request, 'You have successfully subscribed to the tier.')
    return redirect('client:dashboard')


@login_required(login_url='login')
@client_required
def subscriptions(request):
    """
    Display the user's active subscriptions.

    Fetches and displays the active subscriptions of the user.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered subscriptions HTML page with the user's active subscriptions.
    """
    user = request.user
    subscriptions = Subscription.objects.filter(user=user, status='ACTIVE').select_related('tier__user')
    return render(request, 'client/subscriptions.html', {
        'subscriptions': subscriptions,
    })


@login_required(login_url='login')
@client_required
def extend_subscription(request, subscription_id):
    """
    Extend a user's subscription.

    Verifies user wallet balance, deducts points, and extends the subscription.

    Args:
        request: The HTTP request object.
        subscription_id: The ID of the subscription to extend.

    Returns:
        Redirects to the subscriptions page with a success or error message.
    """
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user, status='ACTIVE')
    user = request.user
    tier = subscription.tier

    if user.wallet.balance < tier.points_price:
        messages.error(request, 'You do not have enough points to extend this subscription.')
        return redirect('client:subscriptions')

    user.wallet.balance -= tier.points_price
    user.wallet.save()
    creator = tier.user
    creator.wallet.balance += tier.points_price
    creator.wallet.save()

    subscription.end_date += timezone.timedelta(days=30)
    subscription.save()

    Event.objects.create(
        user=user,
        event_type='SUBSCRIPTION_EXTENDED',
        description=f'Extended subscription to {creator.username}\'s {tier.name} tier.'
    )

    Event.objects.create(
        user=creator,
        event_type='SUBSCRIPTION_EXTENDED',
        description=f'{user.username} extended their subscription to your {tier.name} tier.'
    )

    messages.success(request, 'You have successfully extended the subscription.')
    return redirect('client:subscriptions')


@login_required(login_url='login')
@client_required
def cancel_subscription(request, subscription_id):
    """
    Cancel a user's subscription.

    Sets the subscription status to 'CANCELLED' and creates relevant events.

    Args:
        request: The HTTP request object.
        subscription_id: The ID of the subscription to cancel.

    Returns:
        Redirects to the subscriptions page with a success message.
    """
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user, status='ACTIVE')
    subscription.status = 'CANCELLED'
    subscription.save()

    Event.objects.create(
        user=request.user,
        event_type='SUBSCRIPTION_CANCELLED',
        description=f'Cancelled subscription to {subscription.tier.user.username}\'s {subscription.tier.name} tier.'
    )

    Event.objects.create(
        user=subscription.tier.user,
        event_type='SUBSCRIPTION_CANCELLED',
        description=f'{request.user.username} cancelled their subscription to your {subscription.tier.name} tier.'
    )

    messages.success(request, 'You have successfully cancelled the subscription.')
    return redirect('client:subscriptions')

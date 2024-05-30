from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import creator_required
from .forms import PostForm, MediaForm, TierForm
from account.models import CustomUser, Event
from client.models import Subscription
from .models import Media, Post, Tier
from interactions.models import Like
from django.db.models import Value, CharField
from django.contrib import messages
from django.core.paginator import Paginator


@login_required(login_url='login')
@creator_required
def dashboard(request):
    """
    Display the creator's dashboard with their posts.

    Retrieves posts created by the logged-in creator, paginates them, and renders
    them in the 'creator/dashboard.html' template. Also fetches posts liked by the
    creator for display.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered dashboard page.
    """
    posts_list = Post.objects.filter(user=request.user).annotate(visible=Value(True, output_field=CharField())).order_by('-posted_at')
    paginator = Paginator(posts_list, 10)

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    liked_posts = Like.objects.filter(user=request.user, post__in=posts_list).values_list('post_id', flat=True)

    context = {
        'posts': posts,
        'liked_posts': liked_posts,
        'show_visibility': False
    }
    return render(request, 'creator/dashboard.html', context)


@login_required(login_url='login')
@creator_required
def create_post(request):
    """
    Handle the creation of a new post by the creator.

    If the request method is POST, it validates and saves the post and its associated media files.
    Otherwise, it displays an empty form for creating a post.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered create post page or redirects to the dashboard on successful creation.
    """
    if request.method == 'POST':
        post_form = PostForm(request.POST, user=request.user)
        media_form = MediaForm(request.POST, request.FILES)

        if post_form.is_valid() and media_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            if post.is_free:
                post.tier = None
            post.save()

            files = request.FILES.getlist('files')
            allowed_types = ['image/jpeg', 'image/png', 'video/mp4', 'video/avi']
            for file in files:
                if file.content_type not in allowed_types:
                    media_form.add_error('files', f'Invalid file type: {file.content_type}')
            if media_form.errors:
                post.delete()
                return render(request, 'creator/create_post.html', {
                    'post_form': post_form,
                    'media_form': media_form,
                })
            else:
                Event.objects.create(
                    user=request.user,
                    event_type='POST_CREATED',
                    description=f'Created a new post: {post.title}'
                )

            for file in files:
                Media.objects.create(post=post, file=file)

            return redirect('creator:dashboard')

    else:
        post_form = PostForm(user=request.user)
        media_form = MediaForm()

    return render(request, 'creator/create_post.html', {
        'post_form': post_form,
        'media_form': media_form,
    })


@login_required(login_url='login')
@creator_required
def post_delete(request, post_id):
    """
    Handle the deletion of a post by the creator.

    Deletes the specified post if the logged-in user is the creator of the post.
    Otherwise, displays an error message.

    Args:
        request: The HTTP request object.
        post_id: The ID of the post to be deleted.

    Returns:
        HttpResponse: Redirects to the dashboard page.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.user:
        Event.objects.create(
            user=request.user,
            event_type='POST_DELETED',
            description=f'Deleted a post: {post.title}'
        )
        post.delete()
        messages.success(request, 'Post deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this post.')
    return redirect('creator:dashboard')


@login_required(login_url='login')
@creator_required
def tiers(request):
    """
    Display the creator's tiers with their active subscribers.

    Retrieves tiers created by the logged-in creator and their active subscribers,
    and renders them in the 'creator/tiers.html' template.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered tiers page.
    """
    user_tiers = Tier.objects.filter(user=request.user).order_by('-points_price')

    tiers_with_subscribers = []
    for tier in user_tiers:
        subscribers = tier.subscribers.filter(status='ACTIVE')
        tier_info = {
            'id': tier.id,
            'name': tier.name,
            'points_price': tier.points_price,
            'description': tier.description,
            'message_permission': tier.message_permission,
            'subscribers': subscribers,
            'subscriber_count': subscribers.count(),
        }
        tiers_with_subscribers.append(tier_info)

    return render(request, 'creator/tiers.html', {'tiers': tiers_with_subscribers})


@login_required(login_url='login')
@creator_required
def create_tier(request):
    """
    Handle the creation of a new tier by the creator.

    If the request method is POST, it validates and saves the new tier.
    Otherwise, it displays an empty form for creating a tier.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered create tier page or redirects to the tiers page on successful creation.
    """
    if not request.user.stripe_account_id:
        messages.error(request, "You need to connect your Stripe Account ID before creating a tier.")
        return redirect('update-profile')
    if request.method == 'POST':
        form = TierForm(request.POST, user=request.user)
        if form.is_valid():
            tier = form.save(commit=False)
            tier.user = request.user
            tier.save()
            messages.success(request, 'Tier created successfully.')

            Event.objects.create(
                user=request.user,
                event_type='TIER_CREATED',
                description=f'Created a new tier: {tier.name}'
            )

            return redirect('creator:tiers')
    else:
        form = TierForm(user=request.user)

    return render(request, 'creator/create_tier.html', {'form': form})


@login_required(login_url='login')
@creator_required
def delete_tier(request, tier_id):
    """
    Handle the deletion of a tier by the creator.

    Deletes the specified tier if it has no active subscribers. Otherwise,
    displays an error message.

    Args:
        request: The HTTP request object.
        tier_id: The ID of the tier to be deleted.

    Returns:
        HttpResponse: Redirects to the tiers page.
    """
    tier = get_object_or_404(Tier, id=tier_id, user=request.user)

    if request.method == 'POST':
        active_subscribers = Subscription.objects.filter(tier=tier, status='ACTIVE').exists()

        if active_subscribers:
            messages.error(request, "You cannot delete this tier because it has active subscribers.")
            return redirect('creator:tiers')

        tier.delete()
        Event.objects.create(
            user=request.user,
            event_type='TIER_DELETED',
            description=f'Deleted a tier: {tier.name}'
        )
        messages.success(request, "Tier deleted successfully.")
        return redirect('creator:tiers')

    return render(request, 'creator/tiers.html', {'tier': tier})

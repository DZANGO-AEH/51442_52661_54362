import stripe
from creator.models import Post, Subscription
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Case, When, Value, BooleanField, Q
from django.shortcuts import get_object_or_404, render, redirect
from interactions.models import Like
from django.contrib.auth import update_session_auth_hash

from .forms import CustomUserCreationForm, UserProfileForm, UserPasswordChangeForm, CustomUserUpdateForm
from .helpers import get_active_subscribers_count, get_total_likes, get_total_likes_given, get_total_subscriptions
from .models import UserProfile, CustomUser as User, Event

stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    """
    View for the home page. Redirects authenticated users based on their role.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered home page or a redirect.
    """
    if request.user.is_authenticated:
        if request.user.is_content_creator:
            return redirect('creator:dashboard')
        else:
            return redirect('client:dashboard')
    return render(request, 'account/index.html')


def register(request):
    """
    View for user registration. Handles the registration form and user creation.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered registration page or a redirect.
    """
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your account has been created successfully! You can now login.')

            Event.objects.create(
                user=user,
                event_type='Registration',
                description='Registered a new account'
            )

            return redirect('login')
    context = {'form': form}
    return render(request, 'account/register.html', context)


def userlogin(request):
    """
    View for user login. Handles the authentication form and user login.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered login page or a redirect.
    """
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_content_creator:
                    return redirect('creator:dashboard')
                else:
                    return redirect('client:dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    context = {'form': form}
    return render(request, 'account/login.html', context)


def userlogout(request):
    """
    View for user logout. Logs out the user and redirects to the home page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: A redirect to the home page.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required(login_url='login')
def profile(request, username):
    """
    View for displaying a user's profile. Handles different visibility of posts based on subscription status.

    Args:
        request (HttpRequest): The request object.
        username (str): The username of the profile to view.

    Returns:
        HttpResponse: The rendered profile page.
    """
    user_viewed = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user_viewed)
    is_own_profile = user_viewed == request.user

    user_subscription = Subscription.objects.filter(user=request.user, status='ACTIVE', tier__user=user_viewed).first()

    if is_own_profile:
        posts_list = Post.objects.filter(user=user_viewed).order_by('-posted_at')
        posts_list = posts_list.annotate(visible=Value(True, output_field=BooleanField()))
    else:
        visible_posts = Post.objects.filter(user=user_viewed, is_free=True)
        subscribed_posts = Post.objects.none()

        if user_subscription:
            subscribed_posts = Post.objects.filter(user=user_viewed, tier=user_subscription.tier)

        posts_list = Post.objects.filter(user=user_viewed).annotate(
            visible=Case(
                When(Q(is_free=True) | Q(pk__in=subscribed_posts), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).order_by('-posted_at')

    paginator = Paginator(posts_list, 10)  # 10 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    recipient_subscription = Subscription.objects.filter(user=user_viewed, status='ACTIVE').first()
    can_message = (
            (user_subscription and user_subscription.tier.message_permission) or
            (recipient_subscription and recipient_subscription.tier.message_permission) or
            is_own_profile
    )

    active_subscribers_count = get_active_subscribers_count(user_viewed)
    total_likes = get_total_likes(user_viewed)
    total_likes_given = get_total_likes_given(user_viewed)
    total_subscriptions = get_total_subscriptions(user_viewed)

    liked_posts = Like.objects.filter(user=request.user, post__in=posts_list).values_list('post_id', flat=True)

    return render(request, 'account/profile.html', {
        'user': request.user,
        'user_viewed': user_viewed,
        'profile': user_profile,
        'posts': posts,
        'is_own_profile': is_own_profile,
        'can_message': can_message,
        'active_subscribers_count': active_subscribers_count,
        'total_likes': total_likes,
        'total_likes_given': total_likes_given,
        'total_subscriptions': total_subscriptions,
        'show_visibility': True,
        'liked_posts': liked_posts,
    })


@login_required(login_url='login')
def create_stripe_account(request):
    """
    View for creating a Stripe account for the user.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: A redirect to Stripe account onboarding or a redirect to the update profile page.
    """
    user = request.user
    if not user.stripe_account_id:
        try:
            account = stripe.Account.create(
                type="express",
                country="US",
                email=user.email,
                business_type="individual",
                individual={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                },
                business_profile={
                    "url": f"https://onlyvans.com/profile/{user.username}",
                    "name": user.username
                }
            )
            user.stripe_account_id = account.id
            user.save()

            account_link = stripe.AccountLink.create(
                account=account.id,
                refresh_url=request.build_absolute_uri('/profile/create-stripe-account/'),
                return_url=request.build_absolute_uri('/profile/update/'),
                type='account_onboarding'
            )
            messages.success(request, 'Stripe account created successfully!')
            return redirect(account_link.url)
        except stripe.error.StripeError as e:
            messages.error(request, f"Stripe error: {e}")
    else:
        try:
            account = stripe.Account.retrieve(user.stripe_account_id)
            if account.requirements.currently_due:
                account_link = stripe.AccountLink.create(
                    account=user.stripe_account_id,
                    refresh_url=request.build_absolute_uri('/profile/create-stripe-account/'),
                    return_url=request.build_absolute_uri('/profile/update/'),
                    type='account_onboarding'
                )
                return redirect(account_link.url)
            else:
                messages.info(request, "Stripe account is already fully configured.")
        except stripe.error.StripeError as e:
            messages.error(request, f"Stripe error: {e}")
    return redirect('update-profile')


def update_profile(request):
    user = request.user
    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')

            Event.objects.create(
                user=request.user,
                event_type='Profile Update',
                description='Updated profile'
            )

            return redirect('update-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = CustomUserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=user.profile)

    return render(request, 'account/update_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        password_form = UserPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')

            Event.objects.create(
                user=request.user,
                event_type='Profile Update',
                description='Changed password'
            )

            return redirect('update-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = UserPasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {
        'password_form': password_form
    })

@login_required(login_url='login')
def event_history(request):
    """
    View for displaying the user's event history.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered event history page.
    """
    user = request.user
    events_list = Event.objects.filter(user=user).order_by('-timestamp')

    paginator = Paginator(events_list, 20)
    page_number = request.GET.get('page')
    events = paginator.get_page(page_number)

    return render(request, 'account/event_history.html', {'events': events})

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserProfileForm, UserPasswordChangeForm, CustomUserUpdateForm
from .models import UserProfile, CustomUser as User
from creator.models import Post, Subscription
from django.urls import reverse
from .helpers import get_active_subscribers_count, get_total_likes, get_total_favourites, get_total_subscriptions
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Count, Case, When, Value, BooleanField, Q, CharField, F, Sum
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
import logging

def home(request):
    if request.user.is_authenticated:
        if request.user.is_content_creator:
            return redirect('creator:dashboard')
        else:
            return redirect('client:dashboard')
    return render(request, 'account/index.html')


def register(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully! You can now login.')
            return redirect('login')
    context = {'form': form}
    return render(request, 'account/register.html', context)


def userlogin(request):
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
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('')


logger = logging.getLogger(__name__)


@login_required
def profile(request, username):
    user_viewed = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user_viewed)
    is_own_profile = user_viewed == request.user

    user_subscription = Subscription.objects.filter(user=request.user, status='ACTIVE', tier__user=user_viewed).first()

    if is_own_profile:
        posts = Post.objects.filter(user=user_viewed).order_by('-posted_at')
        posts = posts.annotate(visible=Value(True, output_field=BooleanField()))
    else:
        visible_posts = Post.objects.filter(user=user_viewed, is_free=True)
        subscribed_posts = Post.objects.none()

        if user_subscription:
            subscribed_posts = Post.objects.filter(user=user_viewed, tier=user_subscription.tier)

        posts = Post.objects.filter(user=user_viewed).annotate(
            visible=Case(
                When(Q(is_free=True) | Q(pk__in=subscribed_posts), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).order_by('-posted_at')

    logger.info(f"Count of all posts: {posts.count()}")
    for post in posts:
        logger.info(f"Post: {post.title}, Visible: {post.visible}")

    recipient_subscription = Subscription.objects.filter(user=user_viewed, status='ACTIVE').first()
    can_message = (
        (user_subscription and user_subscription.tier.message_permission) or
        (recipient_subscription and recipient_subscription.tier.message_permission) or
        is_own_profile
    )

    active_subscribers_count = get_active_subscribers_count(user_viewed)
    total_likes = get_total_likes(user_viewed)
    total_favourites = get_total_favourites(user_viewed)
    total_subscriptions = get_total_subscriptions(user_viewed)

    return render(request, 'account/profile.html', {
        'user': request.user,
        'user_viewed': user_viewed,
        'profile': user_profile,
        'posts': posts,
        'is_own_profile': is_own_profile,
        'can_message': can_message,
        'active_subscribers_count': active_subscribers_count,
        'total_likes': total_likes,
        'total_favourites': total_favourites,
        'total_subscriptions': total_subscriptions,
        'show_visibility': True
    })
@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            if user_form.cleaned_data.get('same_email'):
                user.paypal_email = user.email
                user.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('update-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = CustomUserUpdateForm(instance=request.user)
        if request.user.paypal_email == request.user.email:
            user_form.fields['same_email'].initial = True
        profile_form = UserProfileForm(instance=request.user.profile)

    return render(request, 'account/update_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
@login_required
def change_password(request):
    if request.method == 'POST':
        password_form = UserPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('update-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = UserPasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {
        'password_form': password_form
    })

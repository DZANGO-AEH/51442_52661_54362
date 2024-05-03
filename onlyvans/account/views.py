from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserChangeForm, UserProfileForm, UserPasswordChangeForm, CustomUserUpdateForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile, CustomUser
from creator.models import Post
from django.contrib.auth import update_session_auth_hash
from .helpers import get_active_subscribers_count, get_total_likes, get_total_favourites, get_total_subscriptions
from django.contrib import messages


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
            if user is not None and user.is_content_creator:
                login(request, user)
                return redirect('creator:dashboard')
            if user is not None and not user.is_content_creator:
                login(request, user)
                return redirect('client:dashboard')

    context = {'form': form}
    return render(request, 'account/login.html', context)


def userlogout(request):
    logout(request)
    return redirect('')


@login_required
def profile(request, username):
    # Assuming the username is passed via URL, if not, adjust accordingly.
    # If not using usernames, adjust to use id or other unique identifiers.
    username = username  # If URL includes username, replace with appropriate capture.
    try:
        user = CustomUser.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user)
    except (CustomUser.DoesNotExist, UserProfile.DoesNotExist):
        user = request.user
        user_profile = None
    posts = Post.objects.filter(user=request.user).order_by('-posted_at')
    is_own_profile = request.user == user  # Check if the logged-in user is viewing their own profile
    active_subscribers_count = get_active_subscribers_count(user)
    total_likes = get_total_likes(user)
    total_favourites = get_total_favourites(user)
    total_subscriptions = get_total_subscriptions(user)

    return render(request, 'account/profile.html', {
        'user': user,
        'profile': user_profile,
        'is_own_profile': is_own_profile,
        'active_subscribers_count': active_subscribers_count,
        'total_likes': total_likes,
        'total_favourites': total_favourites,
        'total_subscriptions': total_subscriptions,
        'posts': posts
    })

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('update-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = CustomUserUpdateForm(instance=request.user)
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
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('update-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = UserPasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {
        'password_form': password_form
    })
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserProfileForm, UserPasswordChangeForm, CustomUserUpdateForm
from .models import UserProfile, CustomUser
from creator.models import Post
from .helpers import get_active_subscribers_count, get_total_likes, get_total_favourites, get_total_subscriptions
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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


@login_required
def profile(request, username):
    try:
        user = request.user
        user_viewed = CustomUser.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user_viewed)
    except (CustomUser.DoesNotExist, UserProfile.DoesNotExist):
        user_viewed = request.user
        user_profile = None
        messages.error(request, "User profile not found.")
    posts = Post.objects.filter(user=user_viewed).order_by('-posted_at')
    is_own_profile = user_viewed == user
    active_subscribers_count = get_active_subscribers_count(user_viewed)
    total_likes = get_total_likes(user_viewed)
    total_favourites = get_total_favourites(user_viewed)
    total_subscriptions = get_total_subscriptions(user_viewed)
    return render(request, 'account/profile.html', {
        'user':  user,
        'user_viewed': user_viewed,
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

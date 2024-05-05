from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import creator_required
from django.forms import modelformset_factory
from .forms import PostForm, MediaForm, TierForm
from .models import Media, Post, Tier
from django.contrib import messages


def home(request):
    return redirect('creator:dashboard')

@login_required(login_url='login')
@creator_required
def dashboard(request):
    posts = Post.objects.filter(user=request.user).order_by('-posted_at')
    context = {'posts': posts}
    return render(request, 'creator/dashboard.html', context)


@login_required(login_url='login')
@creator_required
def create_post(request):
    if request.method == 'POST':
        print("POST request received")
        post_form = PostForm(request.POST, user=request.user)
        media_form = MediaForm(request.POST, request.FILES)

        if post_form.is_valid() and media_form.is_valid():
            print("Both forms are valid")
            post = post_form.save(commit=False)
            post.user = request.user
            if post.is_free:  # Ensure that tier is not set for free posts
                post.tier = None
            post.save()

            files = request.FILES.getlist('files')
            allowed_types = ['image/jpeg', 'image/png', 'video/mp4', 'video/avi']
            for file in files:
                if file.content_type not in allowed_types:
                    media_form.add_error('files', f'Invalid file type: {file.content_type}')
            if media_form.errors:
                print("Media form errors detected, deleting post")
                post.delete()
                return render(request, 'creator/create_post.html', {
                    'post_form': post_form,
                    'media_form': media_form,
                })

            for file in files:
                Media.objects.create(post=post, file=file)

            print("Post created successfully")
            return redirect('creator:dashboard')
        else:
            print("Form is invalid")
            print("Post form errors:", post_form.errors)
            print("Media form errors:", media_form.errors)

    else:
        post_form = PostForm(user=request.user)
        media_form = MediaForm()

    return render(request, 'creator/create_post.html', {
        'post_form': post_form,
        'media_form': media_form,
    })
@login_required
@creator_required
def tiers(request):
    # Fetch all tiers belonging to the current user
    user_tiers = Tier.objects.filter(user=request.user).order_by('-price').prefetch_related('subscribers')

    # Prepare data to pass to the template
    tiers_with_subscribers = []
    for tier in user_tiers:
        subscribers = tier.subscribers.all()
        tier_info = {
            'name': tier.name,
            'price': tier.price,
            'description': tier.description,
            'message_permission': tier.message_permission,
            'subscribers': subscribers,
            'subscriber_count': subscribers.count(),
        }
        tiers_with_subscribers.append(tier_info)

    return render(request, 'creator/tiers.html', {'tiers': tiers_with_subscribers})

@login_required
@creator_required
def create_tier(request):
    if not request.user.paypal_email:
        messages.error(request, "You need to connect your PayPal account before creating a tier.")
        return redirect('update-profile')
    if request.method == 'POST':
        form = TierForm(request.POST)
        if form.is_valid():
            new_tier = form.save(commit=False)
            new_tier.user = request.user
            new_tier.save()
            return redirect('creator:tiers')
    else:
        form = TierForm()

    return render(request, 'creator/create_tier.html', {'form': form})
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
        post_form = PostForm(request.POST)
        media_form = MediaForm(request.POST, request.FILES)

        # Check if the "is this a free post?" checkbox is checked
        if 'is_free' in request.POST and request.POST['is_free'] == 'on':
            # If it is, remove 'tier' from the list of required fields
            post_form.fields['tier'].required = False

        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()

            files = request.FILES.getlist('files')
            allowed_types = ['image/jpeg', 'image/png', 'video/mp4', 'video/avi']
            for f in files:
                if f.content_type in allowed_types:
                    Media.objects.create(post=post, file=f)
                else:
                    # Handle invalid file type, maybe return an error message
                    pass

            return redirect('creator:dashboard')  # Replace 'dashboard' with the actual name of your view or URL pattern

    else:
        post_form = PostForm()
        media_form = MediaForm()

    return render(request, 'creator/create_post.html', {
        'post_form': post_form,
        'media_form': media_form
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
    if request.method == 'POST':
        form = TierForm(request.POST)
        if form.is_valid():
            new_tier = form.save(commit=False)
            new_tier.user = request.user  # Set the user as the current user
            new_tier.save()
            return redirect('creator:tiers')  # Redirect to the tier overview page
    else:
        form = TierForm()

    return render(request, 'creator/create_tier.html', {'form': form})
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.urls import reverse
from .forms import CustomUserCreationForm, UserProfileForm, UserPasswordChangeForm, CustomUserUpdateForm, PurchasePointsForm, WithdrawPointsForm
from .models import UserProfile, CustomUser as User, Wallet, Transaction
from creator.models import Post, Subscription
from django.conf import settings
from .helpers import get_active_subscribers_count, get_total_likes, get_total_favourites, get_total_subscriptions
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, BooleanField, Q
import logging
import stripe
import time

stripe.api_key = settings.STRIPE_SECRET_KEY
DOLLARS_PER_POINT = 1 / 21.5  # 21.5 points = $1

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
def create_stripe_account(request):
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

@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
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



@login_required(login_url='login')
def purchase_points(request):
    if request.method == 'POST':
        form = PurchasePointsForm(request.POST)
        if form.is_valid():
            points = int(form.cleaned_data['points'])
            amount_in_dollars = points * DOLLARS_PER_POINT
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    mode="payment",
                    customer_email=request.user.email,
                    line_items=[{
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "Purchase Points",
                            },
                            "unit_amount": int(amount_in_dollars * 100),
                        },
                        "quantity": 1,
                    }],
                    success_url=request.build_absolute_uri(reverse("purchase-success")) + "?session_id={CHECKOUT_SESSION_ID}&points=" + str(points),
                    cancel_url=request.build_absolute_uri(reverse("purchase")),
                )
                return redirect(session.url)
            except stripe.error.StripeError as e:
                messages.error(request, f"Stripe error: {str(e)}")
        else:
            messages.error(request, "Invalid amount.")
    else:
        form = PurchasePointsForm()
    return render(request, 'account/purchase_points.html', {'form': form, 'dollars_per_point': DOLLARS_PER_POINT})

@login_required(login_url='login')
def purchase_success(request):
    session_id = request.GET.get("session_id")
    points = int(request.GET.get("points", 0))
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        user = request.user

        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet.balance += points
        wallet.save()

        Transaction.objects.create(
            user=user,
            type='PURCHASE',
            amount=points,
            description='Purchase Points'
        )
        messages.success(request, "Points successfully purchased!")
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {str(e)}")
    return redirect("")

@login_required(login_url='login')
def withdraw_points(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)

    if not user.stripe_account_id:
        messages.warning(request, 'Please update your Stripe account ID before making a withdrawal.')
        return redirect('update-profile')

    account = stripe.Account.retrieve(user.stripe_account_id)
    if 'transfers' not in account.capabilities or account.capabilities['transfers'] != 'active':
        messages.error(request, "Your Stripe account does not have the required capabilities enabled. Try reconnecting your account!")
        return redirect('update-profile')

    if request.method == 'POST':
        form = WithdrawPointsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['points']
            if wallet.balance < amount:
                messages.error(request, "Insufficient points for this withdrawal.")
            else:
                payout_amount = amount * DOLLARS_PER_POINT * 0.5  # 50% fee

                try:
                    stripe.Transfer.create(
                        amount=int(payout_amount * 100),
                        currency='usd',
                        destination=user.stripe_account_id,
                        description='Points Withdrawal'
                    )

                    wallet.balance -= amount
                    wallet.save()
                    Transaction.objects.create(
                        user=user,
                        type='WITHDRAWAL',
                        amount=amount,
                        description='Points Withdrawal'
                    )
                    messages.success(request, "Withdrawal successfully processed!")
                    return redirect('')
                except stripe.error.StripeError as e:
                    messages.error(request, f"Stripe error: {e}")
        else:
            messages.error(request, "Amount is required.")
    else:
        form = WithdrawPointsForm(initial={'points': wallet.balance})

    return render(request, 'account/withdraw_points.html', {'wallet': wallet, 'form': form, 'dollars_per_point': DOLLARS_PER_POINT})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from account.models import CustomUser as User
from creator.models import Tier, Subscription
from django.urls import reverse

from .decorators import client_required
import stripe
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import datetime
import pytz
from django.db import IntegrityError

logger = logging.getLogger(__name__)


@login_required(login_url='login')
@client_required
def dashboard(request):
    return render(request, 'client/dashboard.html')


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
    return create_stripe_subscription(request, tier.id)


@login_required(login_url='login')
@client_required
def create_stripe_subscription(request, tier_id):
    tier = get_object_or_404(Tier, id=tier_id)
    user = request.user

    # Check for existing active subscription
    existing_subscription = Subscription.objects.filter(user=user, tier__user=tier.user, status='ACTIVE').first()
    if existing_subscription:
        messages.error(request, f"You already have an active subscription to {tier.user.username}.")
        return redirect("client:select-tier", username=tier.user.username)

    try:
        # Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=user.email,
            line_items=[{
                "price": tier.stripe_price_id,
                "quantity": 1,
            }],
            success_url=request.build_absolute_uri(reverse("client:stripe-success")) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("client:select-tier", kwargs={"username": tier.user.username})),
            metadata={
                "tier_id": tier_id
            },
        )
        return redirect(session.url)

    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {str(e)}")
        return redirect("client:select-tier", username=tier.user.username)


@login_required(login_url='login')
@client_required
def stripe_success(request):
    session_id = request.GET.get("session_id")
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        subscription = stripe.Subscription.retrieve(session.subscription)
        tier_id = int(session.metadata["tier_id"])
        tier = get_object_or_404(Tier, id=tier_id)
        user = request.user

        # Save the subscription details
        Subscription.objects.create(
            user=user,
            tier=tier,
            stripe_subscription_id=subscription.id,
            status="ACTIVE",
            start_date=datetime.datetime.fromtimestamp(subscription.current_period_start, datetime.timezone.utc),
            end_date=datetime.datetime.fromtimestamp(subscription.current_period_end, datetime.timezone.utc),
        )
        messages.success(request, "Subscription successfully created!")

    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {str(e)}")
    except KeyError as e:
        messages.error(request, f"KeyError: {str(e)}")
    return redirect("client:dashboard")

@login_required(login_url='login')
@client_required
def stripe_cancel(request):
    messages.error(request, "Subscription canceled.")
    return redirect("client:dashboard")


@login_required(login_url='login')
@client_required
def cancel_stripe_subscription(request, username, tier_id):
    tier = get_object_or_404(Tier, id=tier_id, user__username=username, user__is_content_creator=True)
    subscription = get_object_or_404(Subscription, tier=tier, user=request.user)

    try:
        stripe.Subscription.delete(subscription.stripe_subscription_id)
        subscription.status = "CANCELLED"
        subscription.save()
        messages.success(request, "Subscription successfully cancelled.")
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {str(e)}")

    return redirect("profile", username=request.user.username)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponseBadRequest("Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponseBadRequest("Invalid signature")

    if event['type'] == 'checkout.session.completed':
        try:
            session = event['data']['object']
            subscription = stripe.Subscription.retrieve(session['subscription'])
            price_id = subscription['items']['data'][0]['price']['id']
            tier = get_object_or_404(Tier, stripe_price_id=price_id)
            user = User.objects.get(email=session['customer_email'])
            stripe_subscription_id = subscription['id']

            if not Subscription.objects.filter(stripe_subscription_id=stripe_subscription_id).exists():
                # Convert to aware datetime using UTC
                start_date = datetime.datetime.fromtimestamp(
                    subscription['current_period_start'], tz=pytz.UTC)
                end_date = datetime.datetime.fromtimestamp(
                    subscription['current_period_end'], tz=pytz.UTC)

                Subscription.objects.create(
                    user=user,
                    tier=tier,
                    stripe_subscription_id=stripe_subscription_id,
                    status="ACTIVE",
                    start_date=start_date,
                    end_date=end_date,
                )
        except Exception as e:
            logger.error(f"Error processing 'checkout.session.completed': {e}")
            return HttpResponse(status=500)
    elif event['type'] == 'customer.subscription.deleted':
        try:
            subscription = event['data']['object']
            sub = Subscription.objects.get(stripe_subscription_id=subscription['id'])
            sub.status = "CANCELLED"
            sub.save()
        except Exception as e:
            logger.error(f"Error processing 'customer.subscription.deleted': {e}")
            return HttpResponse(status=500)

    return JsonResponse({'status': 'success'})
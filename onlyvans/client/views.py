from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import client_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from account.models import CustomUser
from creator.models import Tier, Subscription
import paypalrestsdk
from django.conf import settings
from datetime import datetime, timedelta


@login_required(login_url='login')
@client_required
def dashboard(request):
    return render(request, 'client/dashboard.html')


@login_required(login_url='login')
@client_required
def select_tier(request, username):
    creator = get_object_or_404(CustomUser, username=username, is_content_creator=True)
    tiers = Tier.objects.filter(user=creator)
    return render(request, 'client/select_tier.html', {'creator': creator, 'tiers': tiers})


@login_required(login_url='login')
@client_required
def subscribe_to_tier(request, username, tier_id):
    creator = get_object_or_404(CustomUser, username=username, is_content_creator=True)
    tier = get_object_or_404(Tier, id=tier_id, user=creator)

    if not creator.paypal_email:
        messages.error(request, f"{creator.username} has not set up a PayPal account.")
        return redirect('profile', username=username)

    return create_paypal_subscription(request, tier.id)


@login_required(login_url='login')
@client_required
def create_paypal_subscription(request, tier_id):
    tier = get_object_or_404(Tier, id=tier_id)

    # Configure PayPal
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET
    })

    # Create a billing plan
    billing_plan = paypalrestsdk.BillingPlan({
        "name": f"Subscription to {tier.name}",
        "description": f"Subscription to {tier.name}",
        "type": "INFINITE",
        "payment_definitions": [{
            "name": f"Regular payment for {tier.name}",
            "type": "REGULAR",
            "frequency": "MONTH",
            "frequency_interval": "1",
            "amount": {
                "value": str(tier.price),
                "currency": "USD"
            },
            "cycles": "0"
        }],
        "merchant_preferences": {
            "auto_bill_amount": "YES",
            "cancel_url": request.build_absolute_uri("/paypal/cancel/"),
            "return_url": request.build_absolute_uri("/paypal/execute/")
        }
    })

    if billing_plan.create():
        # Activate the billing plan
        billing_plan.activate()
        # Create a billing agreement
        billing_agreement = paypalrestsdk.BillingAgreement({
            "name": f"Subscription to {tier.name}",
            "description": f"Subscription to {tier.name}",
            "start_date": (datetime.now() + timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "plan": {
                "id": billing_plan.id
            },
            "payer": {
                "payment_method": "paypal"
            }
        })

        if billing_agreement.create():
            # Redirect the user to PayPal to confirm
            for link in billing_agreement.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            messages.error(request, "Error creating PayPal agreement.")
            return redirect("client:select-tier", username=tier.user.username)
    else:
        messages.error(request, "Error creating PayPal plan.")
        return redirect("client:select-tier", username=tier.user.username)

@login_required(login_url='login')
@client_required
def execute_paypal_subscription(request, username, tier_id):
    token = request.GET.get("token")
    tier = get_object_or_404(Tier, id=tier_id, user__username=username, user__is_content_creator=True)
    if token:
        agreement = paypalrestsdk.BillingAgreement.execute(token)

        if agreement.state == "Active":
            subscription = Subscription.objects.create(
                user=request.user,
                tier=tier,
                paypal_subscription_id=agreement.id,
                status='ACTIVE',
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30)
            )
            messages.success(request, "Subscription successfully created!")
        else:
            messages.error(request, "Subscription failed.")
    else:
        messages.error(request, "Subscription token not provided.")

    return redirect("profile", username=request.user.username)


@login_required(login_url='login')
@client_required
def cancel_paypal_subscription(request, username, tier_id):
    tier = get_object_or_404(Tier, id=tier_id, user__username=username, user__is_content_creator=True)
    subscription = get_object_or_404(Subscription, tier=tier, user=request.user)
    agreement = paypalrestsdk.BillingAgreement.find(subscription.paypal_subscription_id)
    if agreement.cancel({"note": "Cancelling the subscription"}):
        subscription.status = "CANCELLED"
        subscription.save()
        messages.success(request, "Subscription successfully cancelled.")
    else:
        messages.error(request, "Failed to cancel subscription.")

    return redirect("profile", username=request.user.username)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from account.models import Event
from .models import Wallet, Transaction
from .forms import PurchasePointsForm, WithdrawPointsForm
import stripe
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
DOLLARS_PER_POINT = 1 / 21.5  # 21.5 points = $1

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
        Event.objects.create(
            user=user,
            event_type='Purchase',
            description=f'Purchased {points} points'
        )
        messages.success(request, "Points successfully purchased!")
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {str(e)}")
    return redirect("home")

@login_required(login_url='login')
def withdraw_points(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)

    if not user.stripe_account_id:
        messages.warning(request, 'Please update your Stripe account ID before making a withdrawal.')
        return redirect('update-profile')

    try:
        account = stripe.Account.retrieve(user.stripe_account_id)
        if 'transfers' not in account.capabilities or account.capabilities['transfers'] != 'active':
            messages.error(request, "Your Stripe account does not have the required capabilities enabled. Try reconnecting your account!")
            return redirect('update-profile')
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error while retrieving account: {e}")
        messages.error(request, f"Stripe error: {e}")
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

                    wallet.balance -= amount  # Zmniejszenie salda przeniesione do bloku try
                    wallet.save()
                    Transaction.objects.create(
                        user=user,
                        type='WITHDRAWAL',
                        amount=amount,
                        description='Points Withdrawal'
                    )
                    messages.success(request, "Withdrawal successfully processed!")

                    Event.objects.create(
                        user=user,
                        event_type='Withdrawal',
                        description=f'Withdrew {amount} points'
                    )

                    return redirect('home')
                except stripe.error.StripeError as e:
                    logger.error(f"Stripe error while processing transfer: {e}")
                    messages.error(request, f"Stripe error: {e}")
        else:
            messages.error(request, "Amount is required.")
    else:
        form = WithdrawPointsForm(initial={'points': wallet.balance})

    return render(request, 'account/withdraw_points.html', {'wallet': wallet, 'form': form, 'dollars_per_point': DOLLARS_PER_POINT})
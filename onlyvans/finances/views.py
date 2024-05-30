import stripe
from account.models import Event
from client.decorators import client_required
from creator.decorators import creator_required
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import PurchasePointsForm, WithdrawPointsForm
from .models import Wallet, Transaction

stripe.api_key = settings.STRIPE_SECRET_KEY
dollars_per_point = settings.DOLLARS_PER_POINT


@login_required(login_url='login')
@client_required
def purchase_points(request):
    """
    Handles the purchase of points by the user. Displays a form to enter the number of points to purchase,
    processes the payment using Stripe, and redirects to the Stripe checkout session.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the purchase points form or redirects to the Stripe checkout session.
    """
    if request.method == 'POST':
        form = PurchasePointsForm(request.POST)
        if form.is_valid():
            points = int(form.cleaned_data['points'])
            amount_in_dollars = points * dollars_per_point
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
                    success_url=request.build_absolute_uri(
                        reverse("purchase-success")) + "?session_id={CHECKOUT_SESSION_ID}&points=" + str(points),
                    cancel_url=request.build_absolute_uri(reverse("purchase")),
                )
                return redirect(session.url)
            except stripe.error.StripeError as e:
                messages.error(request, f"Stripe error: {str(e)}")
        else:
            messages.error(request, "Invalid amount.")
    else:
        form = PurchasePointsForm()
    return render(request, 'finances/purchase_points.html', {'form': form, 'dollars_per_point': dollars_per_point})


@login_required(login_url='login')
@client_required
def purchase_success(request):
    """
    Handles the successful purchase of points. Updates the user's wallet balance, creates a transaction record,
    and logs the event.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to the home page with a success message.
    """
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
        messages.error(request, f"Payment error: {str(e)}")
    return redirect("home")


@login_required(login_url='login')
@creator_required
def withdraw_points(request):
    """
    Handles the withdrawal of points by the user. Displays a form to enter the number of points to withdraw,
    processes the withdrawal using Stripe, and updates the user's wallet balance.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the withdrawal form or redirects to the home page with a success message.
    """
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)

    if not user.stripe_account_id:
        messages.warning(request, 'Please update your Stripe account ID before making a withdrawal.')
        return redirect('update-profile')

    try:
        account = stripe.Account.retrieve(user.stripe_account_id)
        if 'transfers' not in account.capabilities or account.capabilities['transfers'] != 'active':
            messages.error(request,
                           "Your Stripe account does not have the required capabilities enabled. Try reconnecting your account!")
            return redirect('update-profile')
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {e}")
        return redirect('update-profile')

    if request.method == 'POST':
        form = WithdrawPointsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['points']
            if wallet.balance < amount:
                messages.error(request, "Insufficient points for this withdrawal.")
            else:
                payout_amount = amount * dollars_per_point * 0.5  # 50% fee

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

                    Event.objects.create(
                        user=user,
                        event_type='Withdrawal',
                        description=f'Withdrew {amount} points'
                    )

                    return redirect('home')
                except stripe.error.StripeError as e:
                    messages.error(request, f"Stripe error: {e}")
        else:
            messages.error(request, "Amount is required.")
    else:
        form = WithdrawPointsForm(initial={'points': wallet.balance})

    return render(request, 'finances/withdraw_points.html',
                  {'wallet': wallet, 'form': form, 'dollars_per_point': dollars_per_point})

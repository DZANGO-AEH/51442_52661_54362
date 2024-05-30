from django.utils import timezone
from .models import Subscription
from account.models import Event

def renew_subscriptions():
    """
    Function to renew subscriptions that are due for renewal.
    This function checks all active subscriptions that have reached their end date and attempts to renew them
    if the user has enough points in their wallet. If the user does not have enough points, the subscription is marked as expired.
    """
    now = timezone.now()  # Get the current time with timezone support

    # Get all active subscriptions that have reached their end date
    subscriptions = Subscription.objects.filter(status='ACTIVE', end_date__lte=now)

    for subscription in subscriptions:
        user = subscription.user
        tier = subscription.tier

        # Check if the user has enough points to renew the subscription
        if user.wallet.balance >= tier.points_price:
            # Deduct points from the user's wallet
            user.wallet.balance -= tier.points_price
            user.wallet.save()

            # Add points to the creator's wallet
            creator = tier.user
            creator.wallet.balance += tier.points_price
            creator.wallet.save()

            # Extend the subscription for another 30 days
            subscription.start_date = now
            subscription.end_date = now + timezone.timedelta(days=30)
            subscription.save()

            # Create subscription event for the user
            Event.objects.create(
                user=user,
                event_type='SUBSCRIPTION',
                description=f'Subscribed to {creator.username}\'s {tier.name} tier for another 30 days.'
            )

            # Create subscription event for the creator
            Event.objects.create(
                user=creator,
                event_type='SUBSCRIPTION',
                description=f'{user.username} renewed subscription to your {tier.name} tier for another 30 days.'
            )
        else:
            # If the user does not have enough points, mark the subscription as expired
            subscription.status = 'EXPIRED'
            subscription.save()

            # Create expired subscription event for the user
            Event.objects.create(
                user=user,
                event_type='SUBSCRIPTION',
                description=f'Subscription to {creator.username}\'s {tier.name} tier expired.'
            )

            # Create expired subscription event for the creator
            Event.objects.create(
                user=creator,
                event_type='SUBSCRIPTION',
                description=f'{user.username} subscription to your {tier.name} tier expired.'
            )

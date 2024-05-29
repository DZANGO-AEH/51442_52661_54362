from django.utils import timezone
from account.models import CustomUser as User
from creator.models import Subscription
from account.models import Event
import datetime

def renew_subscriptions():
    now = timezone.now()  # Pobieramy aktualny czas z uwzględnieniem strefy czasowej
    subscriptions = Subscription.objects.filter(status='ACTIVE')


    subscriptions = Subscription.objects.filter(status='ACTIVE', end_date__lte=now)

    for subscription in subscriptions:
        user = subscription.user
        tier = subscription.tier


        if user.wallet.balance >= tier.points_price:
            # Deduct points from user's wallet
            user.wallet.balance -= tier.points_price
            user.wallet.save()

            # Add points to creator's wallet
            creator = tier.user
            creator.wallet.balance += tier.points_price
            creator.wallet.save()

            # Extend the subscription
            subscription.start_date = now
            subscription.end_date = now + timezone.timedelta(days=30)
            subscription.save()

            Event.objects.create(
                user=user,
                event_type='SUBSCRIPTION',
                description=f'Subscribed to {creator.username}\'s {tier.name} tier for another 30 days.'
            )

            Event.objects.create(
                user=creator,
                event_type='SUBSCRIPTION',
                description=f'{user.username} renewed subscription to your {tier.name} tier for another 30 days.'
            )

        else:
            # Deactivate the subscription
            subscription.status = 'EXPIRED'
            subscription.save()

            Event.objects.create(
                user=user,
                event_type='SUBSCRIPTION',
                description=f'Subscription to {creator.username}\'s {tier.name} tier expired.'
            )

            Event.objects.create(
                user=creator,
                event_type='SUBSCRIPTION',
                description=f'{user.username} subscription to your {tier.name} tier expired.'
            )


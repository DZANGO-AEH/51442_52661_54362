from django.utils import timezone
from account.models import CustomUser as User
from creator.models import Subscription
import datetime

def renew_subscriptions():
    now = timezone.now()  # Pobieramy aktualny czas z uwzględnieniem strefy czasowej
    subscriptions = Subscription.objects.filter(status='ACTIVE')
    for subscription in subscriptions:
        print(subscription.end_date)

    subscriptions = Subscription.objects.filter(status='ACTIVE', end_date__lte=now)

    for subscription in subscriptions:
        user = subscription.user
        tier = subscription.tier

        print(f'Processing subscription for user: {user.username}, tier: {tier.name}')

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

            print(f'Subscription for user: {user.username} renewed.')
        else:
            # Deactivate the subscription
            subscription.status = 'EXPIRED'
            subscription.save()

            print(f'Subscription for user: {user.username} expired.')

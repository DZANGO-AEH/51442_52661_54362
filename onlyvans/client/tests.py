from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from creator.models import Tier, Subscription, Post
from account.models import Wallet, Transaction
from django.urls import reverse
import datetime

User = get_user_model()


class SubscriptionTests(TestCase):

    def setUp(self):
        self.creator = User.objects.create_user(username='creator', password='password', is_content_creator=True)
        self.user = User.objects.create_user(username='user', password='password')

        # Create wallets for users
        self.creator_wallet = Wallet.objects.create(user=self.creator, balance=0)
        self.user_wallet = Wallet.objects.create(user=self.user, balance=1000)  # Give the user some points

        # Create a tier
        self.tier = Tier.objects.create(
            name='Gold',
            points_price=100,
            description='Gold Tier',
            user=self.creator,
            message_permission=True
        )

    def test_create_tier(self):
        self.assertEqual(Tier.objects.count(), 1)
        tier = Tier.objects.first()
        self.assertEqual(tier.name, 'Gold')
        self.assertEqual(tier.points_price, 100)
        self.assertEqual(tier.description, 'Gold Tier')
        self.assertEqual(tier.user, self.creator)


    def test_subscribe_to_tier(self):
        self.client.login(username='user', password='password')

        self.client.get(reverse('client:subscribe-to-tier', args=[self.creator.username, self.tier.id]))
        self.user.refresh_from_db()
        self.creator.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, 900)
        self.assertEqual(self.creator.wallet.balance, 100)

        response = self.client.get(reverse('client:subscribe-to-tier', args=[self.creator.username, self.tier.id]))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(str(message) == 'You already have an active subscription to this creator.' for message in messages))

    def test_renew_subscription(self):
        # Subscribe to the tier
        now = timezone.now()
        subscription = Subscription.objects.create(
            user=self.user,
            tier=self.tier,
            status='ACTIVE',
            start_date=now,
            end_date=now + timezone.timedelta(days=30)
        )

        def advance_time(days):
            subscription.end_date -= timezone.timedelta(days=days)
            subscription.save()

        def renew_subscriptions():
            subscriptions = Subscription.objects.filter(status='ACTIVE', end_date__lte=timezone.now())
            for subscription in subscriptions:
                user = subscription.user
                tier = subscription.tier
                if user.wallet.balance >= tier.points_price:
                    user.wallet.balance -= tier.points_price
                    user.wallet.save()
                    creator = tier.user
                    creator.wallet.balance += tier.points_price
                    creator.wallet.save()
                    subscription.start_date = timezone.now()
                    subscription.end_date = timezone.now() + timezone.timedelta(days=30)
                    subscription.save()
                else:
                    subscription.status = 'EXPIRED'
                    subscription.save()

            # Test renewing after 5 days (should not renew yet)
            advance_time(5)
            renew_subscriptions()
            subscription.refresh_from_db()
            self.assertEqual(subscription.status, 'ACTIVE')
            self.assertEqual(subscription.end_date, now + timezone.timedelta(days=25))  # 30 - 5 days
            self.user.refresh_from_db()
            self.creator.refresh_from_db()
            self.assertEqual(self.user.wallet.balance, 900)
            self.assertEqual(self.creator.wallet.balance, 100)

            # Test renewing after 20 more days (total 25 days, should not renew yet)
            advance_time(20)
            renew_subscriptions()
            subscription.refresh_from_db()
            self.assertEqual(subscription.status, 'ACTIVE')
            self.assertEqual(subscription.end_date, now + timezone.timedelta(days=5))  # 30 - 25 days
            self.user.refresh_from_db()
            self.creator.refresh_from_db()
            self.assertEqual(self.user.wallet.balance, 900)
            self.assertEqual(self.creator.wallet.balance, 100)

            # Test renewing after 5 more days (total 30 days, should renew)
            advance_time(5)
            renew_subscriptions()
            subscription.refresh_from_db()
            self.assertEqual(subscription.status, 'ACTIVE')
            self.assertEqual(subscription.end_date, now + timezone.timedelta(days=30))  # Renewed for another 30 days
            self.user.refresh_from_db()
            self.creator.refresh_from_db()
            self.assertEqual(self.user.wallet.balance, 800)
            self.assertEqual(self.creator.wallet.balance, 200)

            # Test renewing after 5 more days (total 35 days, should still be active and not renewed for another 30 days)
            advance_time(5)
            renew_subscriptions()
            subscription.refresh_from_db()
            self.assertEqual(subscription.status, 'ACTIVE')
            self.assertEqual(subscription.end_date, now + timezone.timedelta(days=25))  # 30 - 5 days
            self.creator.refresh_from_db()
            self.assertEqual(self.user.wallet.balance, 800)
            self.assertEqual(self.creator.wallet.balance, 200)



class PurchasePointsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')

        # Create wallet for user
        self.user_wallet = Wallet.objects.create(user=self.user, balance=100)

    def test_purchase_points(self):
        self.assertEqual(self.user.wallet.balance, 100)

        # Simulate purchase of points
        points_to_add = 500
        self.user.wallet.balance += points_to_add
        self.user.wallet.save()

        # Log the transaction
        Transaction.objects.create(
            user=self.user,
            type='PURCHASE',
            amount=points_to_add,
            description='Purchased points'
        )

        # Check balances and transaction
        self.user.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, 600)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.type, 'PURCHASE')
        self.assertEqual(transaction.amount, 500)
        self.assertEqual(transaction.description, 'Purchased points')



class WithdrawPointsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password', is_content_creator=True)
        self.user.stripe_account_id = 'acct_test'  # Simulate that user has a Stripe account ID
        self.user.save()

        # Create wallet for user
        self.user_wallet = Wallet.objects.create(user=self.user, balance=1000)

    def test_withdraw_points(self):
        self.assertEqual(self.user.wallet.balance, 1000)

        # Simulate withdrawal of points
        points_to_withdraw = 500
        payout_amount = points_to_withdraw * 0.5  # Simulate 50% fee

        # Deduct points from user's wallet
        self.user.wallet.balance -= points_to_withdraw
        self.user.wallet.save()

        # Log the transaction
        Transaction.objects.create(
            user=self.user,
            type='WITHDRAWAL',
            amount=points_to_withdraw,
            description='Points withdrawal'
        )

        # Check balances and transaction
        self.user.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, 500)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.type, 'WITHDRAWAL')
        self.assertEqual(transaction.amount, 500)
        self.assertEqual(transaction.description, 'Points withdrawal')

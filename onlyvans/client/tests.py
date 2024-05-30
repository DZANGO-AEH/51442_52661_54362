from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from creator.models import Tier
from .models import Subscription
from finances.models import Wallet
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()

class ClientTests(TestCase):

    def setUp(self):
        """
        Set up test data for each test case. This includes creating a client user,
        a creator user, a tier, and wallets for both users.
        """
        self.client_user = User.objects.create_user(
            username='clientuser',
            email='client@example.com',
            password='password123',
            is_content_creator=False
        )
        self.creator_user = User.objects.create_user(
            username='creatoruser',
            email='creator@example.com',
            password='password123',
            is_content_creator=True
        )
        self.tier = Tier.objects.create(
            user=self.creator_user,
            name='Gold',
            description='Access to exclusive content',
            points_price=1000
        )
        self.wallet_client = Wallet.objects.create(user=self.client_user, balance=2000)
        self.wallet_creator = Wallet.objects.create(user=self.creator_user, balance=500)

    def test_dashboard(self):
        """
        Test the dashboard view to ensure it loads correctly for a logged-in client user.
        """
        self.client.login(username='clientuser', password='password123')
        response = self.client.get(reverse('client:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/dashboard.html')

    def test_discover_creators(self):
        """
        Test the discover creators view to ensure it loads correctly for a logged-in client user.
        """
        self.client.login(username='clientuser', password='password123')
        response = self.client.get(reverse('client:discover_creators'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/discover_creators.html')

    def test_select_tier(self):
        """
        Test the select tier view to ensure it loads correctly for a given creator.
        """
        self.client.login(username='clientuser', password='password123')
        response = self.client.get(reverse('client:select-tier', kwargs={'username': self.creator_user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/select_tier.html')

    def test_subscribe_to_tier(self):
        """
        Test subscribing to a tier, ensuring the subscription is created and balances are updated.
        """
        self.client.login(username='clientuser', password='password123')
        response = self.client.post(reverse('client:subscribe-to-tier', kwargs={'username': self.creator_user.username, 'tier_id': self.tier.id}))
        self.assertRedirects(response, reverse('client:dashboard'))
        subscription = Subscription.objects.get(user=self.client_user, tier=self.tier)
        self.assertEqual(subscription.status, 'ACTIVE')
        self.client_user.refresh_from_db()
        self.creator_user.refresh_from_db()
        self.assertEqual(self.client_user.wallet.balance, 1000)
        self.assertEqual(self.creator_user.wallet.balance, 1500)

    def test_subscriptions(self):
        """
        Test the subscriptions view to ensure it displays active subscriptions correctly.
        """
        self.client.login(username='clientuser', password='password123')
        Subscription.objects.create(
            user=self.client_user,
            tier=self.tier,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        response = self.client.get(reverse('client:subscriptions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/subscriptions.html')

    def test_extend_subscription(self):
        """
        Test extending a subscription to ensure the end date and wallet balances are updated correctly.
        """
        self.client.login(username='clientuser', password='password123')
        subscription = Subscription.objects.create(
            user=self.client_user,
            tier=self.tier,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        initial_client_balance = self.client_user.wallet.balance
        initial_creator_balance = self.creator_user.wallet.balance

        response = self.client.post(reverse('client:extend_subscription', kwargs={'subscription_id': subscription.id}))
        self.assertRedirects(response, reverse('client:subscriptions'))

        subscription.refresh_from_db()
        self.client_user.refresh_from_db()
        self.creator_user.refresh_from_db()

        self.assertEqual(subscription.end_date, subscription.start_date + timezone.timedelta(days=60))
        self.assertEqual(self.client_user.wallet.balance, initial_client_balance - self.tier.points_price)
        self.assertEqual(self.creator_user.wallet.balance, initial_creator_balance + self.tier.points_price)

    def test_cancel_subscription(self):
        """
        Test canceling a subscription to ensure its status is updated to 'CANCELLED'.
        """
        self.client.login(username='clientuser', password='password123')
        subscription = Subscription.objects.create(
            user=self.client_user,
            tier=self.tier,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        response = self.client.post(reverse('client:cancel_subscription', kwargs={'subscription_id': subscription.id}))
        self.assertRedirects(response, reverse('client:subscriptions'))
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'CANCELLED')

    def test_subscription_model_validation(self):
        """
        Test the validation logic of the Subscription model to ensure invalid subscriptions are caught.
        """
        subscription = Subscription(
            user=self.client_user,
            tier=self.tier,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() - timezone.timedelta(days=1)  # Invalid end date
        )
        with self.assertRaises(ValidationError):
            subscription.clean()

    def test_subscription_unique_constraint(self):
        """
        Test the unique constraint of the Subscription model to prevent multiple active subscriptions to the same tier.
        """
        Subscription.objects.create(
            user=self.client_user,
            tier=self.tier,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        duplicate_subscription = Subscription(
            user=self.client_user,
            tier=self.tier,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        with self.assertRaises(ValidationError):
            duplicate_subscription.clean()

    def test_wallet_balance_deduction(self):
        """
        Test that subscribing to a tier correctly deducts points from the client's wallet.
        """
        initial_balance = self.client_user.wallet.balance
        self.client.login(username='clientuser', password='password123')
        self.client.post(reverse('client:subscribe-to-tier', kwargs={'username': self.creator_user.username, 'tier_id': self.tier.id}))
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.wallet.balance, initial_balance - self.tier.points_price)

    def test_wallet_balance_insufficient(self):
        """
        Test subscribing to a tier when the client's wallet balance is insufficient.
        """
        self.client_user.wallet.balance = 500  # Not enough points to subscribe
        self.client_user.wallet.save()
        self.client.login(username='clientuser', password='password123')
        response = self.client.post(reverse('client:subscribe-to-tier', kwargs={'username': self.creator_user.username, 'tier_id': self.tier.id}))
        self.assertRedirects(response, reverse('client:select-tier', kwargs={'username': self.creator_user.username}))
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.wallet.balance, 500)  # Balance should remain unchanged
        self.assertFalse(Subscription.objects.filter(user=self.client_user, tier=self.tier).exists())

from django.test import TestCase
from django.contrib.auth import get_user_model
from creator.models import Tier, Subscription
from account.models import Wallet
from .views import has_messaging_permission
from django.utils import timezone


User = get_user_model()

class MessagingPermissionTests(TestCase):

    def setUp(self):
        self.creator = User.objects.create_user(username='creator', password='password', is_content_creator=True)
        self.user = User.objects.create_user(username='user', password='password')

        # Create wallets for users
        self.creator_wallet = Wallet.objects.create(user=self.creator, balance=0)
        self.user_wallet = Wallet.objects.create(user=self.user, balance=1000)

        # Create tiers
        self.tier_with_permission = Tier.objects.create(
            name='Gold',
            points_price=100,
            description='Gold Tier',
            user=self.creator,
            message_permission=True
        )

        self.tier_without_permission = Tier.objects.create(
            name='Silver',
            points_price=50,
            description='Silver Tier',
            user=self.creator,
            message_permission=False
        )

        # Create subscriptions
        self.subscription_with_permission = Subscription.objects.create(
            user=self.user,
            tier=self.tier_with_permission,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )

        self.subscription_without_permission = Subscription.objects.create(
            user=self.user,
            tier=self.tier_without_permission,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )

    def test_has_messaging_permission_with_permission(self):
        self.assertTrue(has_messaging_permission(self.user, self.creator))

    def test_has_messaging_permission_without_permission(self):
        self.subscription_with_permission.delete()  # Remove the subscription with permission
        self.assertFalse(has_messaging_permission(self.user, self.creator))

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Post, Tier
from finances.models import Wallet
from client.models import Subscription
from django.utils import timezone

User = get_user_model()

class CreatorTests(TestCase):
    """
    Test cases for the creator application, covering views, models, and constraints.
    """

    def setUp(self):
        """
        Set up test data for the tests. This includes creating a content creator user,
        a client user, their wallets, and a subscription tier.
        """
        self.creator_user = User.objects.create_user(
            username='creatoruser',
            email='creator@example.com',
            password='password123',
            is_content_creator=True,
            stripe_account_id='acct_test123'  # Ensure the Stripe account ID is set
        )
        self.client_user = User.objects.create_user(
            username='clientuser',
            email='client@example.com',
            password='password123',
            is_content_creator=False
        )
        self.wallet_creator = Wallet.objects.create(user=self.creator_user, balance=1000)
        self.wallet_client = Wallet.objects.create(user=self.client_user, balance=2000)

        self.tier = Tier.objects.create(
            user=self.creator_user,
            name='Gold',
            points_price=1000,
            description='Access to exclusive content',
        )

    def test_dashboard(self):
        """
        Test the creator dashboard view.
        """
        self.client.login(username='creatoruser', password='password123')
        response = self.client.get(reverse('creator:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'creator/dashboard.html')

    def test_create_post(self):
        """
        Test creating a new post.
        """
        self.client.login(username='creatoruser', password='password123')
        response = self.client.post(reverse('creator:create-post'), {
            'title': 'Test Post',
            'text': 'This is a test post.',
            'is_free': False,
            'tier': self.tier.id
        })
        self.assertRedirects(response, reverse('creator:dashboard'))
        post = Post.objects.get(title='Test Post')
        self.assertEqual(post.user, self.creator_user)
        self.assertEqual(post.text, 'This is a test post.')
        self.assertFalse(post.is_free)
        self.assertEqual(post.tier, self.tier)

    def test_tiers(self):
        """
        Test the tiers view.
        """
        self.client.login(username='creatoruser', password='password123')
        response = self.client.get(reverse('creator:tiers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'creator/tiers.html')

    def test_create_tier(self):
        """
        Test creating a new tier.
        """
        self.client.login(username='creatoruser', password='password123')
        response = self.client.post(reverse('creator:create-tier'), {
            'name': 'Silver',
            'points_price': 500,
            'description': 'Access to some exclusive content',
            'message_permission': True,
        })
        self.assertRedirects(response, reverse('creator:tiers'))
        tier = Tier.objects.get(name='Silver')
        self.assertEqual(tier.user, self.creator_user)
        self.assertEqual(tier.points_price, 500)
        self.assertTrue(tier.message_permission)

    def test_create_tier_invalid_price(self):
        """
        Test creating a tier with an invalid price.
        """
        self.client.login(username='creatoruser', password='password123')
        response = self.client.post(reverse('creator:create-tier'), {
            'name': 'Platinum',
            'points_price': -100,  # Invalid price
            'description': 'Access to premium content',
            'message_permission': False,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Price must be greater than zero.')

    def test_delete_tier_with_active_subscribers(self):
        """
        Test deleting a tier with active subscribers.
        """
        subscription = Subscription.objects.create(
            user=self.client_user,
            tier=self.tier,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        self.client.login(username='creatoruser', password='password123')
        response = self.client.post(reverse('creator:delete-tier', kwargs={'tier_id': self.tier.id}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You cannot delete this tier because it has active subscribers.")

    def test_post_delete(self):
        """
        Test deleting a post.
        """
        self.client.login(username='creatoruser', password='password123')
        post = Post.objects.create(
            user=self.creator_user,
            title='Test Post',
            text='This is a test post.',
            is_free=False,
            tier=self.tier
        )
        response = self.client.post(reverse('creator:post_delete', kwargs={'post_id': post.id}))
        self.assertRedirects(response, reverse('creator:dashboard'))
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_subscription_creation(self):
        """
        Test creating a subscription.
        """
        subscription = Subscription.objects.create(
            user=self.client_user,
            tier=self.tier,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        self.assertEqual(subscription.user, self.client_user)
        self.assertEqual(subscription.tier, self.tier)
        self.assertEqual(subscription.status, 'ACTIVE')

    def test_tier_unique_constraint(self):
        """
        Test the unique constraint for tiers.
        """
        with self.assertRaises(Exception):
            Tier.objects.create(
                user=self.creator_user,
                name='Gold',
                points_price=2000,
                description='Another tier with the same name'
            )

    def test_invalid_post_creation(self):
        """
        Test creating a post with invalid data.
        """
        self.client.login(username='creatoruser', password='password123')
        response = self.client.post(reverse('creator:create-post'), {
            'title': '',
            'text': 'This is an invalid post with no title.',
            'is_free': False,
            'tier': self.tier.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def test_wallet_balance_insufficient(self):
        """
        Test subscription with insufficient wallet balance.
        """
        self.client_user.wallet.balance = 500  # Not enough points to subscribe
        self.client_user.wallet.save()
        self.client.login(username='clientuser', password='password123')
        response = self.client.post(reverse('client:subscribe-to-tier', kwargs={'username': self.creator_user.username, 'tier_id': self.tier.id}))
        self.assertRedirects(response, reverse('client:select-tier', kwargs={'username': self.creator_user.username}))
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.wallet.balance, 500)  # Balance should remain unchanged
        self.assertFalse(Subscription.objects.filter(user=self.client_user, tier=self.tier).exists())

from django.test import TestCase
from django.contrib.auth import get_user_model
from creator.models import Tier, Post
from client.models import Subscription
from finances.models import Wallet
from .models import Thread, Message, Like
from .helpers import has_messaging_permission
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

class MessagingPermissionTests(TestCase):
    """
    Test cases for checking messaging permissions between users based on their subscriptions.
    """

    def setUp(self):
        """
        Set up test data for messaging permission tests.
        Creates a content creator user, a regular user, wallets, tiers, and subscriptions.
        """
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
        """
        Test that messaging permission is granted when the user has a valid subscription with messaging permission.
        """
        self.assertTrue(has_messaging_permission(self.user, self.creator))

    def test_has_messaging_permission_without_permission(self):
        """
        Test that messaging permission is denied when the user does not have a valid subscription with messaging permission.
        """
        self.subscription_with_permission.delete()  # Remove the subscription with permission
        self.assertFalse(has_messaging_permission(self.user, self.creator))


class ThreadMessageTests(TestCase):
    """
    Test cases for creating and managing message threads between users.
    """

    def setUp(self):
        """
        Set up test data for thread and message tests.
        Creates two users, a thread between them, and messages in the thread.
        """
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

        self.thread = Thread.objects.create()
        self.thread.participants.add(self.user1, self.user2)

        self.message1 = Message.objects.create(thread=self.thread, sender=self.user1, body='Hello user2!')
        self.message2 = Message.objects.create(thread=self.thread, sender=self.user2, body='Hello user1!')

    def test_thread_creation(self):
        """
        Test that a thread is correctly created with two participants.
        """
        self.assertEqual(self.thread.participants.count(), 2)
        self.assertIn(self.user1, self.thread.participants.all())
        self.assertIn(self.user2, self.thread.participants.all())

    def test_message_creation(self):
        """
        Test that messages are correctly created and associated with the thread.
        """
        self.assertEqual(self.thread.messages.count(), 2)
        self.assertIn(self.message1, self.thread.messages.all())
        self.assertIn(self.message2, self.thread.messages.all())

    def test_get_other_participant(self):
        """
        Test that the correct other participant is retrieved from the thread.
        """
        self.assertEqual(self.thread.get_other_participant(self.user1), self.user2)
        self.assertEqual(self.thread.get_other_participant(self.user2), self.user1)


class LikeTests(TestCase):
    """
    Test cases for liking and unliking posts.
    """

    def setUp(self):
        """
        Set up test data for like tests.
        Creates a user, a content creator, a tier, and a post.
        """
        self.user = User.objects.create_user(username='user', password='password')
        self.creator = User.objects.create_user(username='creator', password='password', is_content_creator=True)

        self.tier = Tier.objects.create(
            user=self.creator,
            name='Gold',
            points_price=100,
            description='Gold Tier'
        )

        self.post = Post.objects.create(
            user=self.creator,
            title='Test Post',
            text='This is a test post.',
            is_free=True
        )

        # Ensure the post starts without any likes
        self.post.likes.all().delete()

    def test_like_creation(self):
        """
        Test that a like is correctly created for a post.
        """
        like = Like.objects.create(user=self.user, post=self.post)
        self.assertEqual(self.post.likes.count(), 1)
        self.assertIn(like, self.post.likes.all())

    def test_like_post_view(self):
        """
        Test that the like post view correctly likes a post.
        """
        self.client.login(username='user', password='password')
        response = self.client.post(reverse('like_post', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)

    def test_unlike_post_view(self):
        """
        Test that the like post view correctly unlikes a post.
        """
        self.client.login(username='user', password='password')
        # Initially like the post
        response = self.client.post(reverse('like_post', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)

        # Unlike the post
        response = self.client.post(reverse('like_post', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['likes_count'], 0)

    def test_double_like_post_view(self):
        """
        Test that liking a post twice correctly unlikes the post.
        """
        self.client.login(username='user', password='password')
        # Like the post twice
        response = self.client.post(reverse('like_post', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('like_post', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['likes_count'], 0)

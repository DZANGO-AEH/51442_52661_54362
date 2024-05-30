from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from .models import Wallet, Transaction
from .forms import PurchasePointsForm, WithdrawPointsForm
from django.db.utils import IntegrityError


class FinancesTests(TestCase):

    def setUp(self):
        """
        Set up users, clients, and wallets for testing.
        """
        self.client = Client()

        # Create client user
        self.client_user = get_user_model().objects.create_user(
            username='testclient', password='testpassword', email='client@example.com', is_content_creator=False
        )
        self.client_user.save()
        self.client_wallet = Wallet.objects.create(user=self.client_user, balance=1000)

        # Create creator user
        self.creator_user = get_user_model().objects.create_user(
            username='testcreator', password='testpassword', email='creator@example.com', is_content_creator=True
        )
        self.creator_user.stripe_account_id = 'acct_1234'
        self.creator_user.save()
        self.creator_wallet = Wallet.objects.create(user=self.creator_user, balance=1000)

    def test_purchase_points_view_get(self):
        """
        Test the GET method of the purchase_points view. Ensures the form is displayed correctly for client.
        """
        self.client.login(username='testclient', password='testpassword')

        response = self.client.get(reverse('purchase'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/purchase_points.html')
        self.assertIsInstance(response.context['form'], PurchasePointsForm)

    def test_transaction_model(self):
        """
        Test the Transaction model.
        """
        transaction = Transaction.objects.create(
            user=self.client_user,
            type='PURCHASE',
            amount=100.0,
            description='Test transaction'
        )
        self.assertEqual(transaction.user, self.client_user)
        self.assertEqual(transaction.type, 'PURCHASE')
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.description, 'Test transaction')

    def test_wallet_model(self):
        """
        Test the Wallet model.
        """
        wallet = Wallet.objects.get(user=self.client_user)
        self.assertEqual(wallet.user, self.client_user)
        self.assertEqual(wallet.balance, 1000)

        # Try creating another wallet for the same user and catch the IntegrityError
        with self.assertRaises(IntegrityError):
            Wallet.objects.create(user=self.client_user, balance=500)

    @patch('stripe.checkout.Session.create')
    def test_purchase_points_view_post(self, mock_stripe_create):
        """
        Test the POST method of the purchase_points view. Ensures the form processes correctly for client.
        """
        self.client.login(username='testclient', password='testpassword')

        mock_stripe_create.return_value = MagicMock(url='http://mock.stripe.url')
        form_data = {'points': 1000}
        response = self.client.post(reverse('purchase'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect to Stripe checkout

    @patch('stripe.checkout.Session.retrieve')
    def test_purchase_success_view(self, mock_stripe_retrieve):
        """
        Test the purchase_success view. Ensures points are added to the client's wallet and transaction is recorded.
        """
        self.client.login(username='testclient', password='testpassword')

        mock_stripe_retrieve.return_value = MagicMock(id='cs_test_1234', payment_status='paid')
        session_id = 'cs_test_1234'
        points = 1000
        response = self.client.get(reverse('purchase-success'), {'session_id': session_id, 'points': points})
        self.assertEqual(response.status_code, 302)  # Redirect to home
        self.client_wallet.refresh_from_db()
        self.assertEqual(self.client_wallet.balance, 2000)  # Points added

        transactions = Transaction.objects.filter(user=self.client_user, type='PURCHASE')
        self.assertEqual(transactions.count(), 1)
        self.assertEqual(transactions.first().amount, points)

    @patch('stripe.Account.retrieve')
    def test_withdraw_points_view_get(self, mock_stripe_account_retrieve):
        """
        Test the GET method of the withdraw_points view. Ensures the form is displayed correctly for creator.
        """
        self.client.login(username='testcreator', password='testpassword')

        mock_stripe_account_retrieve.return_value = MagicMock(capabilities={'transfers': 'active'})

        response = self.client.get(reverse('withdraw'))

        if response.status_code == 302:
            redirect_target = response.url
            self.fail(f"Unexpected redirect to {redirect_target} with status code {response.status_code}")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/withdraw_points.html')
        self.assertIsInstance(response.context['form'], WithdrawPointsForm)

    @patch('stripe.Account.retrieve')
    @patch('stripe.Transfer.create')
    def test_withdraw_points_view_post(self, mock_stripe_transfer_create, mock_stripe_account_retrieve):
        """
        Test the POST method of the withdraw_points view. Ensures the form processes correctly for creator.
        """
        self.client.login(username='testcreator', password='testpassword')

        mock_stripe_account_retrieve.return_value = MagicMock(capabilities={'transfers': 'active'})
        mock_stripe_transfer_create.return_value = MagicMock(id='tr_test_1234')

        form_data = {'points': 500}
        response = self.client.post(reverse('withdraw'), data=form_data)

        self.assertEqual(response.status_code, 302)

        self.creator_wallet.refresh_from_db()
        self.assertEqual(self.creator_wallet.balance, 500)  # Points deducted

        transactions = Transaction.objects.filter(user=self.creator_user, type='WITHDRAWAL')
        self.assertEqual(transactions.count(), 1)
        self.assertEqual(transactions.first().amount, 500)


if __name__ == '__main__':
    unittest.main()

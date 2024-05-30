from django.test import TestCase
from django.urls import reverse
from .models import CustomUser, Event


class AccountTests(TestCase):
    """
    Test case for the account application.
    """

    def setUp(self):
        """
        Set up a user and their profile for testing.
        """
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        self.user.is_content_creator = True
        self.user.save()
        # Profile is automatically created by the post_save signal
        self.profile = self.user.profile

    def test_home_view_redirects_authenticated_user(self):
        """
        Test that an authenticated user is redirected to the appropriate dashboard.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirection to dashboard

    def test_register_view(self):
        """
        Test the registration view. Ensures the form is displayed and processes correctly.
        """
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/register.html')

        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'is_content_creator': False
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302, response.content)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_userlogin_view(self):
        """
        Test the login view. Ensures the form is displayed and processes correctly.
        """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

        form_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(reverse('login'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('creator:dashboard')))

    def test_userlogout_view(self):
        """
        Test the logout view. Ensures the user is logged out and redirected.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_profile_view(self):
        """
        Test the profile view. Ensures the profile page is displayed correctly.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile.html')

    def test_update_profile_view(self):
        """
        Test the update profile view. Ensures the form is displayed and processes correctly.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('update-profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/update_profile.html')

        form_data = {
            'email': 'updated@example.com',
            'first_name': 'First',
            'last_name': 'Last'
        }
        profile_form_data = {
            'description': 'Updated description'
        }
        response = self.client.post(reverse('update-profile'), data={**form_data, **profile_form_data})
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.description, 'Updated description')

    def test_change_password_view(self):
        """
        Test the change password view. Ensures the form is displayed and processes correctly.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('change-password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/change_password.html')

        form_data = {
            'old_password': 'testpassword',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        }
        response = self.client.post(reverse('change-password'), data=form_data)
        self.assertEqual(response.status_code, 302, response.content)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_event_history_view(self):
        """
        Test the event history view. Ensures the event history is displayed correctly.
        """
        self.client.login(username='testuser', password='testpassword')
        Event.objects.create(user=self.user, event_type='Test Event', description='This is a test event')
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/event_history.html')
        self.assertContains(response, 'This is a test event')

    def test_create_stripe_account_view(self):
        """
        Test the create Stripe account view. Ensures the Stripe account is created and user is redirected.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('create_stripe_account'))
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.stripe_account_id)

if __name__ == '__main__':
    unittest.main()

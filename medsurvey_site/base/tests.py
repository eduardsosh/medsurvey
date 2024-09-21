from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class RegistrationTest(TestCase):
    def test_registration_success(self):
        """Test that a user can successfully register with matching passwords."""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@email.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Assuming a redirect on success
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_registration_password_mismatch(self):
        """Test that registration fails when passwords do not match."""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@email.com',
            'password1': 'testpassword123',
            'password2': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)  # Assuming form re-render on failure
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_registration_missing_fields(self):
        """Test that registration fails when required fields are missing."""
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': 'test@email.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        })
        self.assertEqual(response.status_code, 200)  # Assuming form re-render on failure
        self.assertFalse(User.objects.filter(username='').exists())

    def test_registration_missing_fields(self):
        """Test that registration fails when email is incorrect form."""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testemail.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        })
        self.assertEqual(response.status_code, 200)  # Assuming form re-render on failure
        self.assertFalse(User.objects.filter(username='').exists())


class LoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testloginuser', password='testpassword123')

    def test_login_success(self):
        """Test that a user can successfully log in with correct credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'testloginuser',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Assuming a redirect on success
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_credentials(self):
        """Test that login fails with incorrect credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'testloginuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Assuming form re-render on failure
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_nonexistent_user(self):
        """Test that login fails for a non-existent user."""
        response = self.client.post(reverse('login'), {
            'username': 'nonexistentuser',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 200)  # Assuming form re-render on failure
        self.assertFalse(response.wsgi_request.user.is_authenticated)
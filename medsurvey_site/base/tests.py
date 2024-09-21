from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class RegistrationTest(TestCase):
    def test_registration_success(self):
        """Test that a user can successfully register with matching passwords."""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Assuming a redirect on success
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_registration_password_mismatch(self):
        """Test that registration fails when passwords do not match."""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)  # Assuming form re-render on failure
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_registration_missing_fields(self):
        """Test that registration fails when required fields are missing."""
        response = self.client.post(reverse('register'), {
            'username': '',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        })
        self.assertEqual(response.status_code, 200)  # Assuming form re-render on failure
        self.assertFalse(User.objects.filter(username='').exists())


class LoginTest(TestCase):
    
    pass
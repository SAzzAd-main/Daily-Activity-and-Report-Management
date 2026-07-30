from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import UserProfile


# ==============================================================================
# MODEL TESTS
# ==============================================================================

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user, bio='Hello World')

    def test_profile_creation(self):
        self.assertEqual(self.profile.bio, 'Hello World')
        self.assertEqual(self.profile.user.username, 'testuser')

    def test_profile_str(self):
        result = str(self.profile)
        self.assertIn('testuser', result)


# ==============================================================================
# VIEW TESTS
# ==============================================================================

class RegisterViewTest(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_new_user(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_valid_user(self):
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_password(self):
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)  # Stays on login page


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_logout(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class ProfileViewTest(TestCase):
    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_loads_when_logged_in(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=user)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

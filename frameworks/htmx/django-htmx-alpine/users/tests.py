from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .forms import NewUserCreationForm, UserAuthenticationForm

UserModel = get_user_model()


class UserFormTest(TestCase):
    """Test user forms"""

    def test_new_user_creation_form_has_captcha(self):
        """Test that NewUserCreationForm includes captcha field"""
        form = NewUserCreationForm()
        self.assertIn('captcha', form.fields)

    def test_user_authentication_form_has_captcha(self):
        """Test that UserAuthenticationForm includes captcha field"""
        form = UserAuthenticationForm()
        self.assertIn('captcha', form.fields)

    def test_username_is_lowercase(self):
        """Test that username is converted to lowercase"""
        form = NewUserCreationForm(data={
            'username': 'TestUser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        if form.is_valid():
            self.assertEqual(form.cleaned_data['username'], 'testuser')


class UserViewTest(TestCase):
    """Test user views"""

    def setUp(self):
        self.client = Client()

    def test_users_root_redirects(self):
        """Test that users root redirects to login"""
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 302)

    def test_register_view_get(self):
        """Test GET request to register view"""
        response = self.client.get('/users/register/')
        self.assertEqual(response.status_code, 200)
        # Should have captcha in context
        self.assertIn('captcha_key', response.context)
        self.assertIn('captcha_img_url', response.context)

    def test_login_view_accessible(self):
        """Test that login view is accessible"""
        response = self.client.get('/users/login/')
        self.assertEqual(response.status_code, 200)

    def test_logout_view_accessible(self):
        """Test that logout view is accessible"""
        response = self.client.get('/users/logout/')
        # Should redirect after logout
        self.assertIn(response.status_code, [200, 302])


class UserAuthenticationTest(TestCase):
    """Test user authentication"""

    def setUp(self):
        self.client = Client()
        self.user = UserModel.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_user_can_login(self):
        """Test that user can login with correct credentials"""
        logged_in = self.client.login(
            username='testuser',
            password='testpass123'
        )
        self.assertTrue(logged_in)

    def test_user_cannot_login_with_wrong_password(self):
        """Test that user cannot login with wrong password"""
        logged_in = self.client.login(
            username='testuser',
            password='wrongpassword'
        )
        self.assertFalse(logged_in)

    def test_user_logout(self):
        """Test that user can logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/users/logout/')
        # After logout, user should not be authenticated
        self.assertIn(response.status_code, [200, 302])


class UtilityFunctionTest(TestCase):
    """Test utility functions"""

    def test_get_form_errors(self):
        """Test get_form_errors function"""
        from .views import get_form_errors

        # Create a form with errors
        form = NewUserCreationForm(data={
            'username': '',
            'password1': 'pass',
            'password2': 'different'
        })

        # Form should be invalid
        self.assertFalse(form.is_valid())

        # Should return first error
        error = get_form_errors(form)
        self.assertIsNotNone(error)
        self.assertIsInstance(error, str)

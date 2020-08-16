from django.urls import reverse, resolve
from django.test import TestCase
from django.contrib.auth import forms as authforms, views as authviews
from django.core import mail
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from . import forms, views, factory, models


class SignUpTest(TestCase):
    def setUp(self) -> None:
        self.data = {"username": "test", "password1": "Testpassword", "password2": "Testpassword", "email": "damkuch@gmail.com"}

    def test_assert_test_data_is_valid(self):
        self.assertTrue(forms.CustomUserCreationForm(data=self.data).is_valid())

    def test_response(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_function(self):
        view = resolve('/user/signup/')
        self.assertEquals(view.func.view_class, views.SignUp)

    def test_create_user(self):
        response = self.client.post(reverse("signup"), self.data)
        self.assertEqual(response.status_code, 302)

        #is User and corresponding Progile created
        user = models.User.objects.get(username="test")
        self.assertTrue(user)

        #is email sent
        self.assertEqual(len(mail.outbox), 1)

    def test_is_activation_link_working(self):
        user = factory.UserFactory()
        self.assertTrue(not user.is_active)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        data = {"user": user.username, "token": token}
        self.client.get(reverse("activate_account", kwargs=data))

        user.refresh_from_db()
        self.assertTrue(user.is_active)


class LoginTest(TestCase):
    def setUp(self) -> None:
        self.data = {"username": "test_user0", "password": "TestPassword", "email": "test@gmial.com"}

    def test_response(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_function(self):
        view = resolve('/user/login/')
        self.assertEquals(view.func.view_class, authviews.LoginView)

    def test_login_user_not_activated_failed(self):
        factory.UserFactory.reset_sequence()
        user_profile_not_activated = factory.UserFactory()
        self.assertTrue(user_profile_not_activated)

        response = self.client.post(reverse("login"), data=self.data)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_login_user_activated_success(self):
        factory.UserFactory.reset_sequence()
        user_profile_activated = factory.UserFactory(is_active=True)
        self.assertTrue(user_profile_activated)

        response = self.client.post(reverse("login"), data=self.data, follow=True)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))


class ResetPasswordTest(TestCase):
    def setUp(self) -> None:
        pass

    def test_response(self):
        response = self.client.get(reverse("get_reset_token"))
        self.assertEqual(response.status_code, 200)

    def test_function(self):
        view = resolve('/user/confirm_emial/')
        self.assertEquals(view.func.view_class, authviews.PasswordResetView)

    def test_get_reset_token(self):
        pass

    def test_reset_email(self):
        pass
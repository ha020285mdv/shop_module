from django.test import TestCase

from ishop.forms import CustomUserCreationForm
from ishop.models import ShopUser


class CustomUserCreationFormTestCase(TestCase):
    def test_valid_form(self):
        data = {'email': 'user@gmail.com', 'password1': 'dkmkiia12', 'password2': 'dkmkiia12'}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_without_email(self):
        data = {'email': '', 'password1': 'dkmkiia12', 'password2': 'dkmkiia12'}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_second_password(self):
        data = {'email': 'user@gmail.com', 'password1': 'dkmkiia12'}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_return_user(self):
        data = {'email': 'user@gmail.com', 'password1': 'dkmkiia12', 'password2': 'dkmkiia12'}
        form = CustomUserCreationForm(data=data)
        user = form.save()
        self.assertTrue(isinstance(user, ShopUser))

    def test_form_if_user_already_exists(self):
        data = {'email': 'user@gmail.com', 'password1': 'dkmkiia12', 'password2': 'dkmkiia12'}
        form1 = CustomUserCreationForm(data=data)
        form1.save()
        form2 = CustomUserCreationForm(data=data)
        self.assertFalse(form2.is_valid())

    def test_form_set_username_from_email(self):
        data = {'email': 'user@gmail.com', 'password1': 'dkmkiia12', 'password2': 'dkmkiia12'}
        form = CustomUserCreationForm(data=data)
        user = form.save()
        self.assertEqual(user.username, data['email'])

    def test_form_set_wallet(self):
        data = {'email': 'user@gmail.com', 'password1': 'dkmkiia12', 'password2': 'dkmkiia12'}
        form = CustomUserCreationForm(data=data)
        user = form.save()
        self.assertEqual(user.wallet, 1000)

    def test_form_set_password(self):
        data = {'email': 'user@gmail.com', 'password1': 'dkmkiia12', 'password2': 'dkmkiia12'}
        form = CustomUserCreationForm(data=data)
        user = form.save()
        self.assertTrue(user.check_password(data['password1']))

from django.test import TestCase
from ishop.models import ShopUser


class ShopUserTestCase(TestCase):
    def setUp(self):
        ShopUser.objects.create(email="123@gmail.com", password="123")

    def test_user_creating(self):
        """Object has created and has attributes"""
        user = ShopUser.objects.get(email="123@gmail.com")
        self.assertEqual(user.email, '123@gmail.com')

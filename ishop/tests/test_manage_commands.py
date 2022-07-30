from django.core.management import call_command
from django.test import TestCase

from ishop.models import ShopUser, Good, Purchase, Refund


class DeclineRefundsTest(TestCase):
    def setUp(self):
        user = ShopUser.objects.create(email="user@gmail.com", password="ghhjggsa10")
        beer = Good.objects.create(title="Beer", price=10, in_stock=10)
        wine = Good.objects.create(title="Wine", price=15, in_stock=20)
        purchase1 = Purchase.objects.create(customer=user, good=beer, quantity=3, price=10)
        purchase2 = Purchase.objects.create(customer=user, good=wine, quantity=4, price=15)
        refund1 = Refund.objects.create(purchase=purchase1)
        refund2 = Refund.objects.create(purchase=purchase2)

    def test_decline_refunds(self):
        call_command('decline_refunds')
        refunds = Refund.objects.all()
        self.assertFalse(refunds)

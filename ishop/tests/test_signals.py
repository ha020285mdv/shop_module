from django.test import TestCase, Client

from Shop.settings import QUANTITY_SIGNALS_AUTO_ADD_GOODS_IN_STOCK_WHEN_GET_RID
from ishop.models import ShopUser, Good, Purchase
from ishop.tests.factories import ShopUserFactory


class SignalAddGoodInStockTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = ShopUserFactory()
        self.user.save()
        self.c.force_login(self.user)
        self.good = Good.objects.create(title="Pen", price=5, in_stock=10)
        self.auto_add = QUANTITY_SIGNALS_AUTO_ADD_GOODS_IN_STOCK_WHEN_GET_RID

    def test_auto_add_in_stock_if_get_rid(self):
        data = {'pk': self.good.pk, 'quantity': 10}
        self.c.post('/purchase/', data)
        self.assertEqual(self.auto_add, Good.objects.get(pk=self.good.pk).in_stock)

    def test_not_auto_add_in_stock_if_not_get_rid(self):
        data = {'pk': self.good.pk, 'quantity': 2}
        self.c.post('/purchase/', data)
        self.assertEqual(self.good.in_stock - data['quantity'], Good.objects.get(pk=self.good.pk).in_stock)

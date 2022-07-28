import datetime
from unittest import mock
from faker import Faker
from django.test import RequestFactory, TestCase, Client
import factory

from ishop.models import ShopUser, Good, Purchase, Refund
from ishop.views import GoodsListView, PurchaseView, PurchaseRefundView, Account


class PurchaseViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = ShopUser.objects.create(email='user@gmail.com', password='top_secret01', wallet=1000)
        self.c.force_login(self.user)
        self.good = Good.objects.create(title="Beer", price=5, in_stock=10)
        self.data = {'pk': self.good.pk, 'quantity': 3}

    def test_create_purchase(self):
        self.c.post('/purchase/', self.data)
        purchase = Purchase.objects.first()

        self.assertEqual(purchase.good, self.good)
        self.assertEqual(purchase.customer, self.user)
        self.assertEqual(purchase.quantity, self.data['quantity'])

    def test_purchase_subtraction_money_from_wallet(self):
        self.c.post('/purchase/', self.data)
        self.assertEqual(ShopUser.objects.get(email='user@gmail.com').wallet, 985)

    def test_purchase_subtraction_good_from_stock(self):
        self.c.post('/purchase/', self.data)
        Good.objects.get(title="Beer")
        self.assertEqual(Good.objects.get(title="Beer").in_stock, 7)

    def test_not_create_purchase_if_user_logout(self):
        self.c.logout()
        self.c.post('/purchase/', self.data)
        purchases = Purchase.objects.all()
        self.assertQuerysetEqual(purchases, [])

    def test_not_create_purchase_if_no_money(self):
        self.user.wallet = 10
        self.user.save()
        self.c.post('/purchase/', self.data)
        purchases = Purchase.objects.all()
        self.assertQuerysetEqual(purchases, [])

    def test_not_create_purchase_if_no_in_stock(self):
        self.good.in_stock = 2
        self.good.save()
        self.c.post('/purchase/', self.data)
        purchases = Purchase.objects.all()
        self.assertQuerysetEqual(purchases, [])


class RefundViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = ShopUser.objects.create(email='user@gmail.com', password='top_secret01', wallet=1000)
        self.c.force_login(self.user)
        self.good = Good.objects.create(title="Whiskey", price=30, in_stock=6)
        self.purchase = Purchase.objects.create(customer=self.user,
                                                good=self.good,
                                                quantity=4,
                                                price=30)

    def test_refund_create(self):
        self.c.post('/refund/', {'pk': self.purchase.pk})
        refund = Refund.objects.get(purchase=self.purchase)
        self.assertEqual(refund.purchase, self.purchase)

    def test_avoid_refund_double_create(self):
        self.c.post('/refund/', {'pk': self.purchase.pk})
        refund1 = Refund.objects.get(purchase=self.purchase)
        self.c.post('/refund/', {'pk': self.purchase.pk})
        refund2 = Refund.objects.get(purchase=self.purchase)
        self.assertEqual(refund1, refund2)

    def test_as_context_manager(self):
        mocked_dt = datetime.datetime(2022, 6, 18, 00, 00, 0)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_dt)):
            purchase = Purchase.objects.create(customer=self.user,
                                               good=self.good,
                                               quantity=4,
                                               price=30)
        self.c.post('/refund/', {'pk': purchase.pk})
        refund = Refund.objects.filter(purchase=purchase)
        self.assertQuerysetEqual(refund, [])


class AdminRefundProcessViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.user1 = ShopUser.objects.create(email='user1@gmail.com',
                                            username='user1@gmail.com',
                                            password='top_secret01',
                                            wallet=1000)
        self.user2 = ShopUser.objects.create(email='user2@gmail.com',
                                            username='user2@gmail.com',
                                            password='top_secret01',
                                            wallet=1000)
        self.superuser = ShopUser.objects.create(email='user3@gmail.com',
                                             username='user3@gmail.com',
                                             password='top_secret01',
                                             is_superuser=True)

        beer = Good.objects.create(title="Beer", price=10, in_stock=10)
        wine = Good.objects.create(title="Wine", price=15, in_stock=20)
        vodka = Good.objects.create(title="Vodka", price=19, in_stock=12)
        rum = Good.objects.create(title="Rum", price=21, in_stock=14)
        cidre = Good.objects.create(title="Cidre", price=5, in_stock=23)

        purchase1 = Purchase.objects.create(customer=self.user1, good=beer, quantity=3, price=10)
        purchase2 = Purchase.objects.create(customer=self.user1, good=wine, quantity=1, price=15)
        purchase3 = Purchase.objects.create(customer=self.user2, good=rum, quantity=2, price=21)
        purchase4 = Purchase.objects.create(customer=self.user2, good=cidre, quantity=3, price=5)
        purchase5 = Purchase.objects.create(customer=self.user2, good=vodka, quantity=1, price=19)

        Refund.objects.create(purchase=purchase1)
        Refund.objects.create(purchase=purchase2)
        Refund.objects.create(purchase=purchase3)
        Refund.objects.create(purchase=purchase4)
        Refund.objects.create(purchase=purchase5)

    def test_availability_for_no_superuser(self):
        self.c.force_login(self.user1)
        response = self.c.post('/admin-refund-process/', data={})
        self.assertEqual(response.status_code, 403)

    def test_decline(self):
        self.c.force_login(self.superuser)
        response = self.c.post('/admin-refund-process/', data={'pk': Refund.objects.get(purchase=self.purchase4).pk,
                                                               'approval': 'decline'})
        self.assertNotIn(Refund.objects.all(), b)


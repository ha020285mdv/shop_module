import datetime
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.test import RequestFactory, TestCase, Client
from ishop.models import ShopUser, Good, Purchase, Refund
from ishop.views import GoodsListView, PurchaseView, PurchaseRefundView, Account, Login, AdminRefundProcessView


class PurchaseViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_method_get(self):
        request = self.factory.get('/purchase/')
        response = PurchaseView.as_view()(request)
        self.assertNotEqual(response.status_code, 200)


class AccountViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = ShopUser.objects.create(email='user1@gmail.com',
                                             username='user1@gmail.com',
                                             password='top_secret01',
                                             wallet=1000)
        self.user2 = ShopUser.objects.create(email='user2@gmail.com',
                                             username='user2@gmail.com',
                                             password='top_secret01',
                                             wallet=1000)

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

        Refund.objects.create(purchase=purchase4)
        Refund.objects.create(purchase=purchase5)

    def test_availability(self):
        request = self.factory.get('/account')
        request.user = self.user1
        response = Account.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_queryset(self):
        request = self.factory.get('/account')
        request.user = self.user1
        view = Account()
        view.request = request
        qs = view.get_queryset()
        self.assertQuerysetEqual(qs, Purchase.objects.filter(customer=self.user1))

    def test_get_context_data_has_refund_possible(self):
        request = self.factory.get('/account')
        request.user = self.user1
        response = Account.as_view()(request)
        context = response.context_data
        self.assertIn('refund_possible', context)

    def test_get_context_data_has_in_refund(self):
        request = self.factory.get('/account')
        request.user = self.user1
        response = Account.as_view()(request)
        context = response.context_data
        self.assertIn('in_refund', context)

    def test_get_context_data_in_refund(self):
        request = self.factory.get('/account')
        request.user = self.user2
        response = Account.as_view()(request)
        context = response.context_data
        in_refund = Refund.objects.filter(purchase__customer=self.user2).values_list('purchase__pk', flat=True)
        self.assertQuerysetEqual(context['in_refund'], in_refund)

    def test_get_context_data_has_balance(self):
        request = self.factory.get('/account')
        request.user = self.user1
        response = Account.as_view()(request)
        context = response.context_data
        self.assertIn('balance', context)

    def test_get_context_data_balance(self):
        request = self.factory.get('/account')
        request.user = self.user1
        response = Account.as_view()(request)
        context = response.context_data
        self.assertEqual(self.user1.wallet, context['balance'])


class AdminRefundProcessViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_availability_for_no_logined(self):
        request = self.factory.get('/admin-refund-process/')
        request.user = AnonymousUser()
        response = AdminRefundProcessView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.get('location'), '/accounts/login/?next=/admin-refund-process/')


class LoginViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = ShopUser.objects.create(email='user1@gmail.com',
                                             username='user1@gmail.com',
                                             password='top_secret01',
                                             wallet=1000)

    def test_availability(self):
        request = self.factory.get('/login')
        request.user = AnonymousUser()
        response = Login.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_success_url(self):
        request = self.factory.post('/login', data={'email': 'user1@gmail.com',
                                                    'password': 'top_secret01'})
        view = Login()
        view.setup(request)
        success_url = view.get_success_url()
        self.assertEqual(success_url, '/')

import datetime
from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.test import TestCase, RequestFactory
from django.utils import timezone

from ishop.models import Purchase, Refund, ShopUser, Good
from ishop.tests.factories import ShopUserFactory, GoodFactory, PurchaseFactory, RefundFactory
from ishop.views import PurchaseView, Account, AdminRefundProcessView, Login


class AccountViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user1 = ShopUserFactory(email="test1@gmail.com")
        self.user1.save()
        self.user2 = ShopUserFactory(email="test2@gmail.com")
        self.user2.save()

        good1 = GoodFactory()
        good1.save()

        self.purchase1 = PurchaseFactory(customer=self.user1, good=good1)
        self.purchase1.save()
        self.purchase2 = PurchaseFactory(customer=self.user1, good=good1)
        self.purchase2.save()
        self.purchase3 = PurchaseFactory(customer=self.user1, good=good1)
        self.purchase3.save()
        self.purchase4 = PurchaseFactory(customer=self.user2, good=good1)
        self.purchase4.save()

        self.refund1 = RefundFactory(purchase=self.purchase1)
        self.refund1.save()
        self.refund2 = RefundFactory(purchase=self.purchase2)
        self.refund2.save()
        self.refund3 = RefundFactory(purchase=self.purchase3)
        self.refund3.save()
        self.refund4 = RefundFactory(purchase=self.purchase4)
        self.refund4.save()

    def test_availability_for_authorized(self):
        request = self.factory.get('/account')
        request.user = self.user1
        response = Account.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_decline_for_unauthorized(self):
        request = self.factory.get('/account')
        request.user = AnonymousUser()
        response = Account.as_view()(request)
        self.assertEqual(response.status_code, 302)

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

    def test_get_context_data_refund_possible(self):
        request = self.factory.get('/account')
        request.user = self.user1
        mocked_dt = timezone.now() - timedelta(hours=1)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_dt)):
            self.purchase3.datetime = timezone.now()
            self.purchase3.save()
        response = Account.as_view()(request)
        context = response.context_data
        qs = Purchase.objects.filter(customer=self.user1).exclude(id=self.purchase3.id)
        self.assertQuerysetEqual(context['refund_possible'], qs)

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
        self.assertEqual(context['balance'], self.user1.wallet)


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


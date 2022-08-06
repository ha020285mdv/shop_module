from datetime import timedelta
from unittest import mock

from django.test import TestCase, RequestFactory
from django.utils import timezone

import Shop.settings
from ishop.API.serializers import PurchaseSerializer, RefundSerializer, ShopUserSerializer
from ishop.models import ShopUser
from ishop.tests.factories import ShopUserFactory, GoodFactory, PurchaseFactory, RefundFactory, SuperUserFactory


class PurchaseSerializerTest(TestCase):
    def setUp(self):
        self.serializer = PurchaseSerializer
        self.user = ShopUserFactory()
        self.user.save()
        self.good = GoodFactory()
        self.good.save()
        self.data_dict = {'customer': self.user.pk,
                          'good': self.good.pk,
                          'quantity': 4,
                          'price': self.good.price
                          }

    def test_serializer_ok(self):
        serializer = self.serializer(data=self.data_dict)
        self.assertTrue(serializer.is_valid())

    def test_serializer_not_enough_money(self):
        self.user.wallet = 100
        self.user.save()
        self.good.price = 300
        self.good.save()
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())

    def test_serializer_not_enough_goods_in_stock(self):
        self.good.in_stock = 2
        self.good.save()
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())


class RefundSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RefundSerializer

        self.admin = SuperUserFactory

        self.user1 = ShopUserFactory()
        self.user1.save()
        self.user2 = ShopUserFactory()
        self.user2.save()
        good = GoodFactory()
        good.save()
        self.purchase1_user1 = PurchaseFactory(customer=self.user1, good=good)
        self.purchase1_user1.save()

    def test_serializer_user_creating_refund_for_own_purchase(self):
        data_dict = {'purchase': self.purchase1_user1.pk}
        self.request = RequestFactory()
        self.request.user = self.user1
        serializer = self.serializer(data=data_dict, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

    def test_serializer_creating_refund_for_not_own_purchase(self):
        data_dict = {'purchase': self.purchase1_user1.pk}
        self.request = RequestFactory()
        self.request.user = self.user2
        serializer = self.serializer(data=data_dict, context={'request': self.request})
        self.assertFalse(serializer.is_valid())

    def test_serializer_admin_creating_refund_for_any_purchase(self):
        data_dict = {'purchase': self.purchase1_user1.pk}
        self.request = RequestFactory()
        self.request.user = self.admin
        serializer = self.serializer(data=data_dict, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

    def test_serializer_time_is_expired(self):
        mocked_dt = timezone.now() - timedelta(minutes=Shop.settings.INTERVAL_TO_REFUND + 1)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked_dt)):
            self.purchase1_user1.datetime = timezone.now()
            self.purchase1_user1.save()
        data_dict = {'purchase': self.purchase1_user1.pk}
        self.request = RequestFactory()
        self.request.user = self.user1
        serializer = self.serializer(data=data_dict, context={'request': self.request})
        self.assertFalse(serializer.is_valid())


class ShopUserSerializerTest(TestCase):
    def setUp(self):
        self.serializer = ShopUserSerializer

    def test_serializer_user_create(self):
        data_dict = {'email': 'super@gmail.com', 'password': 'ya01neskagu'}
        serializer = self.serializer(data=data_dict)
        serializer.is_valid()
        serializer.save()
        self.assertTrue(ShopUser.objects.filter(email='super@gmail.com').exists())

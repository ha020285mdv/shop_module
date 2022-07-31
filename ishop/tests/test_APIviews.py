import json

from django.test import TestCase
from ishop.models import ShopUser, Good, Purchase, Refund
from ishop.tests.factories import ShopUserFactory, SuperUserFactory, GoodFactory, PurchaseFactory, RefundFactory
from rest_framework.test import APIClient


class PurchaseViewSetTest(TestCase):

    def setUp(self):
        self.admin = self.admin = SuperUserFactory()
        self.user = ShopUser.objects.create(email='user@gmail.com',
                                             username='user@gmail.com',
                                             password='top_secret01',
                                             wallet=1000)
        self.user.save()
        self.good = GoodFactory()
        self.good.save()
        self.client = APIClient()
        self.data = {'customer': self.user.pk, 'good': self.good.pk, 'quantity': 5}


    def test_get_purchase_not_admin_no_auth(self):
        response = self.client.get('/api/purchases/')
        self.assertEqual(response.status_code, 401)

    # def test_get_purchase_not_admin_auth(self):
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.get('/api/purchases/')
    #     self.assertEqual(response.status_code, 403)

    def test_create_purchase_auth_user_empty_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/purchases/', data={}, format='json')
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(data['customer'] == data['good'] == data['quantity'] == ["This field is required."])

    def test_create_purchase_admin_empty_data(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/purchases/', data={}, format='json')
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(data['customer'] == data['good'] == data['quantity'] == ["This field is required."])

    def test_create_purchase_auth_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/purchases/', data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        del response.data['id']
        self.assertEqual(response.data, {'customer': self.user.pk,
                                         'good': self.good.pk,
                                         'quantity': self.data['quantity'],
                                         'price': self.good.price
                                         })

    def test_create_purchase_take_user_money(self):
        self.client.force_authenticate(user=self.user)
        wallet_before = self.user.wallet
        response = self.client.post('/api/purchases/', data=self.data, format='json')
        wallet_after = ShopUser.objects.get(pk=self.user.pk).wallet
        self.assertEqual(response.status_code, 201)
        self.assertEqual(wallet_after, wallet_before - self.good.price * self.data['quantity'])

    def test_create_purchase_decrease_in_stock(self):
        self.client.force_authenticate(user=self.user)
        in_stock_before = self.good.in_stock

        response = self.client.post('/api/purchases/', data=self.data, format='json')
        in_stock_after = Good.objects.get(pk=self.good.pk).in_stock
        self.assertEqual(response.status_code, 201)
        self.assertEqual(in_stock_after, in_stock_before - self.data['quantity'])

    def test_create_purchase(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/purchases/', data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['id'], Purchase.objects.first().pk)

    def test_check_user_has_object_permissions(self):
        self.client.force_authenticate(user=self.user)
        p = PurchaseFactory(customer=self.user, good=self.good)
        p.save()
        response = self.client.get(f'/api/purchases/{p.id}/')
        self.assertEqual(response.status_code, 200)

    def test_check_admin_has_object_permissions(self):
        self.client.force_authenticate(user=self.admin)
        p = PurchaseFactory(customer=self.user, good=self.good)
        p.save()
        response = self.client.delete(f'/api/purchases/{p.id}/')
        self.assertEqual(response.status_code, 204)


class RefundViewSetTest(TestCase):

    def setUp(self):
        self.admin = SuperUserFactory()

        self.user1 = ShopUserFactory()
        self.user1.save()
        self.user2 = ShopUserFactory()
        self.user2.save()

        good = GoodFactory()
        good.save()

        self.purchase1_user1 = PurchaseFactory(customer=self.user1, good=good)
        self.purchase1_user1.save()
        self.purchase2_user1 = PurchaseFactory(customer=self.user1, good=good)
        self.purchase2_user1.save()

        self.purchase1_user2 = PurchaseFactory(customer=self.user2, good=good)
        self.purchase1_user2.save()
        self.purchase2_user2 = PurchaseFactory(customer=self.user2, good=good)
        self.purchase2_user2.save()

        self.refund1_user1 = RefundFactory(purchase=self.purchase1_user1)
        self.refund1_user1.save()
        self.refund2_user1 = RefundFactory(purchase=self.purchase2_user1)
        self.refund2_user1.save()

        self.refund1_user2 = RefundFactory(purchase=self.purchase1_user2)
        self.refund1_user2.save()
        self.refund2_user2 = RefundFactory(purchase=self.purchase2_user2)
        self.refund2_user2.save()

        self.client = APIClient()

    def test_get_refunds_not_admin_no_auth(self):
        response = self.client.get('/api/refunds/')
        self.assertEqual(response.status_code, 401)

    def test_get_refunds_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/refunds/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Refund.objects.all().count())

    def test_get_only_own_refunds_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/refunds/')
        self.assertEqual(response.status_code, 200)
        resp_ids = ([d['id'] for d in json.loads(response.content)])
        db_ids = list(Refund.objects.filter(purchase__customer=self.user1).values_list('id', flat=True))
        self.assertEqual(resp_ids, db_ids)

    def test_create_refund_user_empty_data(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/refunds/', data={}, format='json')
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['purchase'], ["This field is required."])

    def test_create_refund(self):
        self.client.force_authenticate(user=self.user1)
        data_to_send = {'purchase': self.purchase2_user1.pk}
        response = self.client.post('/api/refunds/', data=data_to_send, format='json')
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['purchase'], self.purchase2_user1.pk)

    def test_action_decline_not_admin_no_auth(self):
        response = self.client.delete(f'/api/refunds/{self.refund2_user2.id}/decline/')
        self.assertEqual(response.status_code, 401)

    def test_action_decline_auth_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/refunds/{self.refund2_user2.id}/decline/')
        self.assertEqual(response.status_code, 403)

    def test_action_decline_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/refunds/{self.refund2_user2.id}/decline/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Refund.objects.filter(pk=self.refund2_user2.pk).exists())

    def test_action_approve_not_admin_no_auth(self):
        response = self.client.delete(f'/api/refunds/{self.refund2_user2.id}/approve/')
        self.assertEqual(response.status_code, 401)

    def test_action_approve_auth_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/refunds/{self.refund2_user2.id}/approve/')
        self.assertEqual(response.status_code, 403)

    def test_action_approve_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/refunds/{self.refund2_user2.id}/approve/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Refund.objects.filter(pk=self.refund2_user2.pk).exists())
        self.assertFalse(Purchase.objects.filter(pk=self.refund2_user2.purchase.pk).exists())

    def test_action_approve_admin_money_back(self):
        self.client.force_authenticate(user=self.admin)
        wallet_before = ShopUser.objects.get(pk=self.refund2_user2.purchase.customer.pk).wallet
        response = self.client.delete(f'/api/refunds/{self.refund2_user2.id}/approve/')
        wallet_after = ShopUser.objects.get(pk=self.refund2_user2.purchase.customer.pk).wallet
        wallet_after_counted = wallet_before + self.refund2_user2.purchase.price * self.refund2_user2.purchase.quantity
        self.assertEqual(response.status_code, 204)
        self.assertEqual(wallet_after, wallet_after_counted)

    def test_action_approve_admin_good_in_stock_back(self):
        self.client.force_authenticate(user=self.admin)
        in_stock_before = Good.objects.get(pk=self.refund2_user2.purchase.good.pk).in_stock
        response = self.client.delete(f'/api/refunds/{self.refund2_user2.id}/approve/')
        in_stock_after = Good.objects.get(pk=self.refund2_user2.purchase.good.pk).in_stock
        in_stock_after_counted = in_stock_before + self.refund2_user2.purchase.quantity
        self.assertEqual(response.status_code, 204)
        self.assertEqual(in_stock_after, in_stock_after_counted)

import datetime
from unittest import mock
from django.test import TestCase, Client

from ishop.forms import CustomUserCreationForm
from ishop.models import ShopUser, Good, Purchase, Refund


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

    def test_avoid_refund_avoid_double_create(self):
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
        self.user1 = ShopUser.objects.create(email='user1@gmail.com', username='user1@gmail.com', password='top_secret01', wallet=1000)
        self.user2 = ShopUser.objects.create(email='user2@gmail.com', username='user2@gmail.com', password='top_secret01', wallet=1000)
        self.admin = ShopUser.objects.create(email='admin@gmail.com', password='top_secret01', is_superuser=True)
        self.c.force_login(self.admin)
        self.good = Good.objects.create(title="Beer", price=5, in_stock=10)
        self.purchase1 = Purchase.objects.create(customer=self.user1, good=self.good, price=5, quantity=4)
        self.purchase2 = Purchase.objects.create(customer=self.user2, good=self.good, price=5, quantity=1)
        self.refund1 = Refund.objects.create(purchase=self.purchase1)
        self.refund2 = Refund.objects.create(purchase=self.purchase2)

    def test_availability_for_no_superuser(self):
        self.c.logout()
        self.c.force_login(self.user1)
        response = self.c.post('/admin-refund-process/', data={})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.reason_phrase, 'Forbidden')

    def test_admin_decline_refund(self):
        response = self.c.post('/admin-refund-process/', data={'pk': self.refund1.pk, 'approval': 'decline'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.refund1, Refund.objects.all())

    def test_admin_approve_refund_delete_refund_object(self):
        response = self.c.post('/admin-refund-process/', data={'pk': self.refund1.pk, 'approval': 'approve'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.refund1, Refund.objects.all())

    def test_admin_approve_refund_delete_purchase_object(self):
        response = self.c.post('/admin-refund-process/', data={'pk': self.refund1.pk, 'approval': 'approve'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.purchase1, Purchase.objects.all())

    def test_admin_approve_refund_send_money_back(self):
        user_pk = self.user1.pk
        wallet_before = ShopUser.objects.get(pk=user_pk).wallet
        amount_to_refund = self.refund1.purchase.price * self.refund1.purchase.quantity
        wallet_after = wallet_before + amount_to_refund
        self.c.post('/admin-refund-process/', data={'pk': self.refund1.pk, 'approval': 'approve'})
        self.assertEqual(wallet_after, ShopUser.objects.get(pk=user_pk).wallet)

    def test_admin_approve_refund_return_goods_in_stock(self):
        good_pk = self.good.pk
        in_stock_before = Good.objects.get(pk=good_pk).in_stock
        in_stock_after = in_stock_before + self.refund1.purchase.quantity
        self.c.post('/admin-refund-process/', data={'pk': self.refund1.pk, 'approval': 'approve'})
        self.assertEqual(in_stock_after, Good.objects.get(pk=good_pk).in_stock)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.form_data = {'email': 'user_new@gmail.com',
                          'password1': 'j3hgGgd12n',
                          'password2': 'j3hgGgd12n'}
        self.c = Client()

    def test_register_redirect(self):
        form = CustomUserCreationForm(data=self.form_data)
        form.is_valid()
        response = self.c.post('/register/', form.cleaned_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_register_user_created(self):
        form = CustomUserCreationForm(data=self.form_data)
        form.is_valid()
        response = self.c.post('/register/', form.cleaned_data)
        self.assertTrue(ShopUser.objects.filter(email='user_new@gmail.com').exists())

    def test_register_user_logged(self):
        form = CustomUserCreationForm(data=self.form_data)
        form.is_valid()
        response = self.c.post('/register/', form.cleaned_data)
        from django.contrib import auth
        user = auth.get_user(self.c)
        assert user.is_authenticated

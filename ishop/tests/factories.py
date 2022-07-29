import factory
from django.utils import timezone

from ishop.models import ShopUser, Good, Purchase, Refund


class ShopUserFactory(factory.Factory):
    email = factory.Sequence(lambda n: 'user%d@gmail.com' % n)
    username = email
    password = 'topsecret007'
    wallet = 1000

    class Meta:
        model = ShopUser


class SuperUserFactory(ShopUserFactory):
    is_superuser = True


class GoodFactory(factory.Factory):
    title = factory.Sequence(lambda n: 'good%d' % n)
    description = factory.LazyAttribute(lambda obj: 'description of %s' % obj.title)
    price = 10
    in_stock = 12

    class Meta:
        model = Good


class PurchaseFactory(factory.Factory):
    customer = factory.SubFactory(ShopUserFactory)
    good = factory.SubFactory(GoodFactory)
    quantity = 3
    price = 10   # factory.LazyAttribute(lambda obj: '%d' % obj.good.price)   (почему-то выдает в строчном формате)
    datetime = timezone.now()

    class Meta:
        model = Purchase


class RefundFactory(factory.Factory):
    purchase = factory.SubFactory(PurchaseFactory)
    date_created = timezone.now()

    class Meta:
        model = Refund

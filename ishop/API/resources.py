from django.db import transaction
from rest_framework.viewsets import ModelViewSet

from ishop.API.filters import IsOwnerOrAdminFilterBackendForRefund, IsOwnerOrAdminFilterBackendForPurchase
from ishop.API.filters import IsOwnerOrAdminFilterBackendForUser
from ishop.API.serializers import GoodSerializer, ShopUserSerializer, PurchaseSerializer, RefundSerializer
from ishop.models import Good, ShopUser, Purchase, Refund
from ishop.permissions import IsAdminOrReadOnly, IsAdminOrCreateOnly, IsAdminOrCreateOnlyForUsers


class GoodsViewSet(ModelViewSet):
    queryset = Good.objects.all()
    serializer_class = GoodSerializer
    permission_classes = (IsAdminOrReadOnly, )


class ShopUserViewSet(ModelViewSet):
    queryset = ShopUser.objects.all()
    serializer_class = ShopUserSerializer
    filter_backends = [IsOwnerOrAdminFilterBackendForUser]
    permission_classes = (IsAdminOrCreateOnlyForUsers, )


class PurchaseViewSet(ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    filter_backends = [IsOwnerOrAdminFilterBackendForPurchase]
    permission_classes = (IsAdminOrCreateOnly, )

    def perform_create(self, serializer):
        quantity = self.request.data['quantity']
        good = Good.objects.get(pk=self.request.data['good'])
        price = good.price
        customer = ShopUser.objects.get(pk=self.request.data['customer'])
        customer.wallet -= quantity * price
        good.in_stock -= quantity

        with transaction.atomic():
            serializer.save(price=price)
            customer.save()
            good.save()


class RefundViewSet(ModelViewSet):
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer
    filter_backends = [IsOwnerOrAdminFilterBackendForRefund]
    permission_classes = (IsAdminOrCreateOnly, )

    def perform_destroy(self, instance):
        """
        If Delete request contains JSON data "approve = True" - do refund
        if request does not contain data, or "approve = False" - delete refund object only
        """
        is_approved = self.request.data.get('approve')

        if is_approved:
            purchase = instance.purchase
            customer = purchase.customer
            good = purchase.good
            quantity = purchase.quantity
            price = purchase.price

            customer.wallet += quantity * price
            good.in_stock += quantity

            with transaction.atomic():
                customer.save()
                good.save()
                purchase.delete()
                instance.delete()
        else:
            instance.delete()

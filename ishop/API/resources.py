from django.db import transaction
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from ishop.API.filters import IsOwnerOrAdminFilterBackendForRefund, IsOwnerOrAdminFilterBackendForPurchase
from ishop.API.filters import IsOwnerOrAdminFilterBackendForUser
from ishop.API.serializers import GoodSerializer, ShopUserSerializer, PurchaseSerializer, RefundSerializer
from ishop.models import Good, ShopUser, Purchase, Refund
from ishop.API.permissions import IsAdminOrReadOnly, IsAdminOrCreateOnly, IsAdminOrCreateOnlyForUsers


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


class RefundViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):

    queryset = Refund.objects.all()
    serializer_class = RefundSerializer
    filter_backends = [IsOwnerOrAdminFilterBackendForRefund]
    permission_classes = (IsAdminOrCreateOnly, )

    @action(detail=True, methods=['delete'])
    def decline(self, request, *args, **kwargs):
        """
        Deleting refund object only without any affect
        """
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['delete'])
    def approve(self, request, *args, **kwargs):
        """
        Do refund: refund money to wallet and good to stock,
        delete refund and purchase objects
        """
        refund = self.get_object()
        purchase = refund.purchase
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
            refund.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

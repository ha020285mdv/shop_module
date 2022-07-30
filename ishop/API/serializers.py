from rest_framework import serializers
from ishop.models import Good, Purchase, ShopUser, Refund
from ishop.views import PurchaseRefundView


class GoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Good
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'customer', 'good', 'quantity', 'price']

    def validate(self, data):
        """
        Check if user has enough money to buy
        Check if quantity is not greater than number of goods in stock
        """
        if data['customer'].wallet < data['quantity'] * data['good'].price:
            raise serializers.ValidationError("Customer don't have enough money to buy")
        if data['quantity'] > data['good'].in_stock:
            raise serializers.ValidationError("Not enough goods in stock")
        return data


class RefundSerializer(serializers.ModelSerializer):

    class Meta:
        model = Refund
        fields = '__all__'

    def validate_purchase(self, value):
        """
        Check purchase ID that it belongs to user's purchases
        """
        user = self.context['request'].user
        if user.is_superuser:
            return value
        if value not in Purchase.objects.filter(customer=user):
            raise serializers.ValidationError("You can create refunds only for your own purchases")
        return value

    def validate(self, data):
        """
        Check if allowed time to refund didn't run out
        """
        if data['purchase'].datetime < PurchaseRefundView.get_time_to_refund():
            raise serializers.ValidationError("Allowed refund time has been expired")
        return data


class ShopUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)
    wallet = serializers.CharField(read_only=True)

    class Meta:
        model = ShopUser
        fields = ['id', 'email', 'password', 'wallet']

    @staticmethod
    def create(validated_data):
        user = ShopUser.objects.create(email=validated_data['email'],
                                       username=validated_data['email'],
                                       wallet=1000)
        user.set_password(validated_data['password'])
        user.save()
        return user

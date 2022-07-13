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
        """
        if data['customer'].wallet < data['quantity'] * data['good'].price:
            raise serializers.ValidationError("Customer don't have enough money to buy")
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


# serializers below are not used

class PurchaseSerializerWithNested(serializers.ModelSerializer):
    good = GoodSerializer()
    customer = ShopUserSerializer()

    class Meta:
        model = Purchase
        fields = ['customer', 'good', 'quantity', 'price']

    def create(self, validated_data):
        good_data = validated_data.pop('good')
        good = Good.objects.create(**good_data)
        customer_data = validated_data.pop('customer')
        customer = ShopUserSerializer.create(customer_data)
        purchase = Purchase.objects.create(customer=customer, good=good, **validated_data)
        good.save()
        customer.save()
        purchase.save()

        return purchase


class NestedPurchaseForUserSerializer(serializers.ModelSerializer):
    good = GoodSerializer()

    class Meta:
        model = Purchase
        fields = ['good', 'quantity']


class ShopUserSerializerNestedPurchases(serializers.ModelSerializer):
    purchase_set = NestedPurchaseForUserSerializer(many=True)
    password = serializers.CharField(write_only=True)
    wallet = serializers.CharField(read_only=True)

    class Meta:
        model = ShopUser
        fields = ['email', 'password', 'wallet', 'purchase_set']

    def create(self, validated_data):
        purchases_data = validated_data.pop('purchase_set')
        user = ShopUserSerializer.create(validated_data)
        for purchase_data in purchases_data:
            quantity = purchase_data.pop('quantity')
            good = purchase_data['good']
            price = good['price']
            Purchase.objects.create(customer=user,
                                    quantity=quantity,
                                    price=price,
                                    good=Good.objects.create(**good)
                                    )
        return user

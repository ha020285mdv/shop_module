from rest_framework import serializers
from ishop.models import Good, Purchase, ShopUser, Refund


class FormSerializer(serializers.Serializer):
    SEX_CHOICES = ['m', 'f']
    CEFR = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

    name = serializers.CharField(max_length=100, required=True)
    sex = serializers.ChoiceField(choices=SEX_CHOICES, required=True)
    age = serializers.IntegerField(required=True)
    english_level = serializers.ChoiceField(choices=CEFR)

    def validate(self, data):
        sex = data['sex']
        age = data['age']
        lvl = data['english_level']
        is_fit = (sex == 'm' and age >= 20 and lvl in ['C1', 'C2']) or \
                 (sex == 'f' and age >= 22 and lvl in ['B2', 'C1', 'C2'])
        if is_fit:
            return data
        else:
            raise serializers.ValidationError('Never give up and try again later!')


class GoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Good
        fields = '__all__'


class ShopUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    wallet = serializers.CharField(read_only=True)

    class Meta:
        model = ShopUser
        fields = ['email', 'password', 'wallet']

    @staticmethod
    def create(validated_data):
        user = ShopUser.objects.create(email=validated_data['email'],
                                       username=validated_data['email'],
                                       wallet=1000)
        user.set_password(validated_data['password'])
        user.save()
        return user


class PurchaseSerializer(serializers.ModelSerializer):
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

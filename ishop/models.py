from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CASCADE


class ShopUser(AbstractUser):
    email = models.EmailField(max_length=150, blank=False, unique=True)
    wallet = models.PositiveIntegerField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        app_label = 'ishop'


class Good(models.Model):
    title = models.CharField(max_length=150, blank=False)
    description = models.CharField(max_length=250, blank=True)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='img', blank=True)
    in_stock = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.in_stock} - {self.title}'

    class Meta:
        ordering = ['in_stock']


class Purchase(models.Model):
    customer = models.ForeignKey(ShopUser, on_delete=CASCADE)
    good = models.ForeignKey(Good, on_delete=CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.datetime} {self.customer}: {self.quantity * self.price} USD'

    class Meta:
        ordering = ['-datetime']


class Refund(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=CASCADE)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']

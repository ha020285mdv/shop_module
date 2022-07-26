from celery import Celery
from celery import shared_task
from django.db import transaction
from django.utils.timezone import now
from ishop.models import Refund

broker_url = 'redis://localhost'
app = Celery('tasks', broker=broker_url, backend=broker_url)


@shared_task
def delete_all_refunds():
    Refund.objects.all().delete()
    return f'all refunds have been declined at {now()}'


@shared_task
def approve_all_refunds():
    for refund in Refund.objects.all():
        user = refund.purchase.customer
        good = refund.purchase.good
        quantity = refund.purchase.quantity
        price = refund.purchase.price
        user.wallet += price * quantity
        good.in_stock += quantity
        with transaction.atomic():
            user.save()
            good.save()
            refund.purchase.delete()
            refund.delete()
    return f'all refunds have been approved at {now()}'

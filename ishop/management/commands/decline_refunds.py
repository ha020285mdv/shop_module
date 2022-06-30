from django.core.management.base import BaseCommand
from ishop.models import Refund


class Command(BaseCommand):
    help = "Decline all current refund issues"

    def handle(self, *args, **options):
        Refund.objects.all().delete()

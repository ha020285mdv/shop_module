from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Shop.settings')
app = Celery('Shop')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'delete-all-refunds-every-day-evening': {
        'task': 'ishop.tasks.delete_all_refunds',
        'schedule': crontab(hour=18, minute=0),
        'args': ()
    },
}
app.conf.timezone = settings.TIME_ZONE
app.conf.enable_utc = False   # !!!important for crontab

#COMMANDS
#celery -A Shop worker --loglevel=INFO
#celery -A Shop beat -l info

from __future__ import absolute_import

import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daily_fresh.settings')

app = Celery('daily_fresh')

app.config_from_object('daily_fresh.celeryconfig')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()




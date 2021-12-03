"""Initialization of the central celery app instance"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proteins_plus.settings')

app = Celery('proteins_plus')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Standard debug task as per the celery docs"""
    print('Request: {0!r}'.format(self.request))

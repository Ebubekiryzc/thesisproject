from __future__ import absolute_import, unicode_literals
from celery import Celery
from datetime import timedelta
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Celery sınıfından bir nesne oluşturma, argüman olarak bulunduğu dosyayı istiyor:
app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'check_all_prices_10s': {
        'task': 'apps.product.tasks.check_discounts',
        'schedule': timedelta(seconds=10)
    }
}
app.autodiscover_tasks()

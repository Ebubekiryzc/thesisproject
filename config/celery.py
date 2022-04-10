from __future__ import absolute_import, unicode_literals
from celery import Celery
from datetime import timedelta
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Celery sınıfından bir nesne oluşturma, argüman olarak bulunduğu dosyayı istiyor:
app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Burada planlanan taskler bulunuyor.
app.conf.beat_schedule = {
    'check_all_prices': {
        'task': 'apps.product.tasks.check_discounts',
        'schedule': timedelta(seconds=10)
    },
    'scrape_all_reviews': {
        'task': 'apps.product.tasks.scrape_review_task',
        'schedule': timedelta(seconds=10),
        'args': (None,)
    }
}
app.autodiscover_tasks()

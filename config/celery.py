import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
# Celery sınıfından bir nesne oluşturma, argüman olarak bulunduğu dosyayı istiyor:
app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'get_joke_3s': {
        'task': 'apps.product.tasks.get_jokes',
        'schedule': 0.1
    }
}
app.autodiscover_tasks()

from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.product'

    def ready(self):
        import apps.product.signals
        print('Zamanlayıcı başladı...')
        from helpers import scheduler
        scheduler.start(20)

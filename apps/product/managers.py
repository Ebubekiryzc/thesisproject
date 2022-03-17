from django.db import models


class ProductQuerySet(models.QuerySet):
    def get_product_or_none(self, instance_link):
        try:
            product = self.get(product_link=instance_link)
        except:
            product = None
        finally:
            return product

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def safe_get(self, instance_link):
        return self.get_queryset().get_product_or_none(instance_link)

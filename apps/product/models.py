from django.db import models

# Create your models here.


class Product(models.Model):
    product_link = models.CharField(max_length=2048, verbose_name='Ürünün Linki')

    def __str__(self):
        return self.product_link

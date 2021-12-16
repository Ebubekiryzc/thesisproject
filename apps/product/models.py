from django.db import models

# Create your models here.


class Product(models.Model):
    product_link = models.CharField(
        max_length=2048, verbose_name='Ürünün Linki')
    product_description = models.CharField(
        max_length=2048, verbose_name="Ürün Adı")
    product_price = models.CharField(max_length=20, verbose_name="Ürünün Fiyatı")
    # product_picture_source = models.CharField(
    #     max_length=2048, verbose_name="Ürün Resmi")

    def __str__(self):
        return self.product_link

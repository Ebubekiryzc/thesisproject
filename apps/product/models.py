from django.db import models
from helpers.models import TrackingModel
from apps.account.models import User

# Create your models here.


class Product(TrackingModel):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product_link = models.CharField(
        max_length=2048, verbose_name='Ürünün Linki')
    product_description = models.CharField(
        max_length=2048, verbose_name="Ürün Adı")
    product_original_price = models.CharField(max_length=20, verbose_name="Ürünün Orijinal Fiyatı")
    product_discounted_price = models.CharField(max_length=20, verbose_name="Ürünün İndirimli Fiyatı")
    product_picture_source = models.CharField(
        max_length=2048, verbose_name="Ürün Resmi")

    def __str__(self):
        return self.product_link


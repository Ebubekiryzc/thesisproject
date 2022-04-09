from email.policy import default
from django.db import models
from apps.product.managers import ProductManager
from helpers.models import TrackingModel


# Create your models here.

class Product(TrackingModel):
    product_link = models.CharField(
        max_length=2048, verbose_name='Ürünün Linki')
    product_description = models.CharField(
        max_length=2048, verbose_name="Ürün Adı")
    product_original_price = models.CharField(
        max_length=20, verbose_name="Ürünün Orijinal Fiyatı")
    product_discounted_price = models.CharField(
        max_length=20, verbose_name="Ürünün İndirimli Fiyatı")
    product_picture_source = models.CharField(
        max_length=2048, verbose_name="Ürün Resmi")
    product_mean_rating = models.CharField(
        max_length=5, verbose_name="Ürünün Değerlendirme Ortalaması")
    product_review_count = models.CharField(
        max_length=30, verbose_name="Ürünün Değerlendirme Sayısı")

    objects = ProductManager()
    will_be_scraped = True

    def __str__(self):
        return self.product_link


class Review(TrackingModel):
    body = models.TextField()
    processed_data = models.JSONField(verbose_name='İşlenmiş metin', default=list, null=True, blank=True)
    sentiment_state = models.SmallIntegerField(verbose_name='Duygu Bilgisi', null=True, blank=True)
    product = models.ForeignKey(
        to=Product, verbose_name='Ürün', blank=True, null=True, on_delete=models.CASCADE)
    updated_by = None

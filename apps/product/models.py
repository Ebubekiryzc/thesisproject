from django.db import models

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=255, verbose_name='Ürün Adı')
    product_detail = models.TextField(max_length=1000, verbose_name='Ürün Detayları')
    product_price = models.DecimalField(verbose_name='Ürün Fiyatı')
    # product_links = models.JSONField()
    
    
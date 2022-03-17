from djongo import models as djongomodels
from django.db import models
from apps.product.managers import ProductManager
from helpers.models import TrackingModel


# Create your models here.
class Review(TrackingModel):
    body = models.TextField()
    updated_by = None

    class Meta:
        abstract = True


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
    product_reviews = djongomodels.ArrayField(
        verbose_name='Yorumlar', model_container=Review, blank=True, null=True)
    _id = djongomodels.ObjectIdField()

    objects = ProductManager()
    will_be_scraped = True

    def __str__(self):
        return self.product_link

    # def save(self, *args, **kwargs):
    #     # Ürün oluşturuluyor mu? Eğer yeniyse zaten scraping metodları oluşturmamıştır
    #     if self.pk is None:

    #         # Ürün zaten mevcutta olan bir ürün mü?
    #         if Product.objects.filter(product_link=self.product_link).exists():

    #             # Bu ürün kullanıcılar tarafından oluşturulduysa
    #             if self.updated_by is not None:
    #                 user_id = self.updated_by

    #                 # Eğer varsa, şu an bu ürünü ekleyen kullanıcı istek listesine eklemiş miydi? Birden fazla kez eklemesini önlüyoruz.
    #                 if Product.objects.filter(users_added_to_wishlist__in=[user_id]).exists():
    #                     print(user_id)
    #                     pass

    #                 # Eğer bu ürün varsa ama kullanıcı bunu istek listesine eklemediyse eklemesini sağlıyoruz.
    #                 else:
    #                     try:
    #                         self.users_added_to_wishlist.append()
    #                     except:
    #                         print(type(self.users_added_to_wishlist))
    #                     super(Product, self).save(*args, **kwargs)

    #         # Bu ürün tabloda yoksa ve yeni bir ürünse hem oluşturuyoruz hem de kullanıcıyı istek listesine ekliyoruz.
    #         else:
    #             if self.updated_by is not None:
    #                 user_id = self.updated_by
    #                 self.users_added_to_wishlist.append(*user_id)
    #             super(Product, self).save(*args, **kwargs)

    #     # Update ediliyorsa (admin, scraping)
    #     else:
    #         super(Product, self).save(*args, **kwargs)

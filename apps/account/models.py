from djongo import models as djongomodels
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken


from apps.product.models import Product

# Create your models here.


class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    products_added_to_wishlist = djongomodels.ArrayReferenceField(
        verbose_name="İstek Listesine Eklenmiş Ürünler", to=Product, on_delete=djongomodels.DO_NOTHING, null=True, blank=True)

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def __str__(self):
        return self.username
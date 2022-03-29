from djongo import models as djongomodels
from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.product.models import Product

# Create your models here.


class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    products_added_to_wishlist = djongomodels.ArrayReferenceField(
        verbose_name="İstek Listesine Eklenmiş Ürünler", to=Product, on_delete=djongomodels.DO_NOTHING, null=True, blank=True)


def __str__(self):
    return " ".join(self.first_name, self.last_name)

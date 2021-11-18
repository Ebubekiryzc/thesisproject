from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    wishlisted_products = models.JSONField(default={'product_id': []})

    def __str__(self):
        return self.email

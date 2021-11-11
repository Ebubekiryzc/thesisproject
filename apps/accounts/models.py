from django.db import models

# Create your models here.


class User(models.Model):
    UserId = models.AutoField(primary_key=True)
    UserName = models.CharField(max_length=100)
    Email = models.EmailField(max_length=320)
    Password = models.CharField(max_length=100)
    IsActive = models.BooleanField(default=True)

    def __str__(self):
        return self.UserName

from django.db import models


class TrackingModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        "account.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)

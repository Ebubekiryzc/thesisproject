from django import forms
from django.core import exceptions
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_link', ]

    def clean(self):
        product_link = self.cleaned_data.get('product_link')

        validator = URLValidator()
        try:
            validator(product_link)
        except ValidationError as e:
            raise exceptions.ValidationError(e.args[0])

        values = {
            "product_link": product_link
        }

        return values

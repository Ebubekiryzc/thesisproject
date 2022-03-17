from django import template

register = template.Library()


@register.filter(name="getRatingPercentage")
def getRatingPercentage(product_mean_rating):
    rating = product_mean_rating
    rating = rating.replace(',', '.')
    rating = float(rating)
    ratingPercentage = str(rating*20)+"%"
    return ratingPercentage

    
@register.filter(name='private')
def private(obj, attribute):
    return getattr(obj, attribute)
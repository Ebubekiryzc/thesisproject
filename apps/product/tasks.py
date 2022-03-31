from __future__ import absolute_import, unicode_literals
from celery import shared_task

from helpers.utils import SScraper, change_url_to_company_name

from .models import Product, Review
from .views import check_all_product_prices


@shared_task
def check_discounts():
    check_all_product_prices()
    return None


def scrape_reviews(product):
    review_scraper = SScraper()
    reviews = getattr(SScraper, f'get_reviews_from_{change_url_to_company_name(product.product_link)}')(review_scraper,
                                                                                                        product.product_link)
    return reviews


def find_new_review_count(registered, unregistered):
    return len(registered) - len(unregistered)


def insert_reviews(reviews, product_id):
    pass


@shared_task
def scrape_review_for_all_products(products=Product.objects.all()):
    if products != Product.objects.all():
        products = list(products)
    for product in products:
        reviews = scrape_reviews(product)
        registered_reviews = Review.objects.filter(product=product)
        new_review_count = find_new_review_count(registered_reviews, reviews)

from __future__ import absolute_import, unicode_literals
from atexit import register
from concurrent.futures.thread import _worker
from celery import shared_task

from helpers.utils import SScraper, change_url_to_company_name

from .models import Product, Review


@shared_task
def check_discounts():
    from .views import check_all_product_prices
    check_all_product_prices()
    return None


def scrape_reviews(product):
    review_scraper = SScraper()
    reviews = getattr(SScraper, f'get_reviews_from_{change_url_to_company_name(product.product_link)}')(review_scraper,
                                                                                                        product.product_link)
    return reviews


def find_new_review_count(registered, unregistered):
    return len(unregistered) - len(registered)


def insert_reviews(raw_datas, product):
    for raw_data in raw_datas:
        review = Review()
        review.product = product
        review.body = raw_data
        review.save()
    # Burada mail yollanabilir.


@shared_task
def scrape_review_task(products):
    if products is None:
        products = list(Product.objects.all())
    elif len(products) == 1:
        products = list(Product.objects.filter(id=products))

    for product in products:
        reviews = scrape_reviews(product)
        print(f'product reviews\n{product} -- {len(reviews)}')
        registered_reviews = Review.objects.filter(product=product)
        new_review_count = find_new_review_count(registered_reviews, reviews)
        if new_review_count > 0:
            insert_reviews(reviews[-new_review_count:], product)

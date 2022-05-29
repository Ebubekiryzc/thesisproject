from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.conf import settings
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from numpy import negative

from helpers.utils import SScraper, change_url_to_company_name
from helpers.sentimentalAnalyzer.deepLearning.sentimentAnalyzerDeepLearning import predict, preprocess_text

from .models import Product, Review
from apps.account.models import User


@shared_task
def check_discounts():
    from .views import check_all_product_prices
    check_all_product_prices()
    return None


def process_text(text):
    return preprocess_text(text)


def predict_sentiment(text):
    return predict(text)


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


def send_email_message(context, users, subject, template_url):
    email_subject = f'{subject}'
    html_email_body = render_to_string(
        f'{template_url}', context)
    email = EmailMessage(subject=email_subject, body=html_email_body, from_email=settings.EMAIL_HOST_PASSWORD,
                         to=[users.email])
    email.content_subtype = 'html'
    email.send()


def extract_sentiment_count_from_reviews(reviews):
    negatives = list()
    positives = list()

    for review in reviews:
        if (review.sentiment_state == 0):
            negatives.append(review)
        else:
            positives.append(review)

    return len(negatives), len(positives)


@shared_task
def send_complete_mail(user_id, product_id):
    product = Product.objects.get(id=product_id)
    reviews = product.review_set.all()
    negative_count, positive_count = extract_sentiment_count_from_reviews(
        reviews)

    happy_percentage = positive_count / (negative_count + positive_count) * 100

    user = User.objects.get(id=user_id)
    context = {
        'product': product,
        'negative_count': negative_count,
        'positive_count': positive_count,
        'happy_percentage': happy_percentage,
    }
    subject = f"Yorum analizi tamamlandı."
    template_url = f"product/product-review-scrape-complete.html"
    send_email_message(context, user, subject, template_url)


@shared_task
def analyze_reviews(user_id, product_id):
    product = Product.objects.get(id=product_id)
    reviews = product.review_set.all()
    for review in reviews:
        review.processed_data = process_text(review.body)
        review.sentiment_state = predict(review.processed_data)
        review.save()

    send_complete_mail.delay(user_id, product_id)


@shared_task
def scrape_review_task(products, user):
    if products is None:
        products = Product.objects.all()
    elif len(products) == 1:
        products = list(Product.objects.filter(id=products))

    for product in products:
        reviews = scrape_reviews(product)
        registered_reviews = Review.objects.filter(product=product)

        new_review_list = list()
        for review in reviews:
            equality = False
            for registered_review in registered_reviews:
                if (review == registered_review.body):
                    equality = True
                    break
            if (equality == False):
                new_review_list.append(review)

        insert_reviews(new_review_list, product)

    if len(products) == 1:
        products = products[0].id
    else:
        products = products.values_list("id", flat=True)

    if user is not None:
        analyze_reviews.delay(user, products)

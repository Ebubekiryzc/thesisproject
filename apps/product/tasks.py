import requests
from celery import shared_task
from .models import Review

@shared_task
def get_jokes():
    # url = 'http://api.icndb.com/jokes/1'
    # response = requests.get(url).json()
    # joke = response['value']['joke']
    Review.objects.create(body='selamke denemeler')
    # return joke
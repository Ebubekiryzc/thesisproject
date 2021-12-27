from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail.message import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from urllib.parse import urlparse

from apps.account.models import User
from .models import Product
from .forms import ProductForm

import requests
import random

# Create your views here.

postcodes = [
    "SW1A 1AA",
    "PE35 6EB",
    "CV34 6AH",
    "EH1 2NG"
]


def schedule_api():

    postcode = postcodes[random.randint(0, 3)]

    full_url = f"https://api.postcodes.io/postcodes/{postcode}"

    r = requests.get(full_url)
    if r.status_code == 200:

        result = r.json()["result"]

        lat = result["latitude"]
        lng = result["longitude"]

        print(f'Latitude: {lat}, Longitude: {lng}')


def index(request):
    return render(request, 'product/index.html')


def about(request):
    return render(request, 'product/about.html')


@login_required(login_url='apps.account:login')
def dashboard(request):
    currentUser = User.objects.filter(id=request.user.id).first()

    products = Product.objects.filter(
        id__in=currentUser.wishlisted_products['product_id'])
    products = list(products)

    itemExist = True
    if len(products) == 0:
        itemExist = False

    favicons = list()

    for product in products:
        product.id = urlsafe_base64_encode(force_bytes(product.id))
        favicons.append(get_favicon(product.product_link))

    content = zip(products, favicons)

    context = {
        "content": content,
        "itemExist": itemExist
    }

    return render(request, 'product/dashboard.html', context)


# TODO: Bir ürün bir kullanıcıya birden fazla kez tanımlanabiliyor.
@login_required(login_url='apps.account:login')
def add_product(request):
    form = ProductForm(request.POST or None)
    context = {
        'form': form
    }

# TODO: Herkes kendi clientında url kontrolü yapsın. Client-side da yapmalıyız.
    if form.is_valid():
        product_link = form.cleaned_data.get("product_link")
        description = ""
        image_source = ""
        price = 0

        if (urlparse(product_link).netloc == "www.trendyol.com"):
            scraped_data = get_html_content_from_trendyol(product_link)
            description = scraped_data["description"]
            price = scraped_data["price"]
            image_source = scraped_data["image"]

        elif (urlparse(product_link).netloc == "www.hepsiburada.com"):
            scraped_data = get_html_content_from_hepsiburada(product_link)
            description = scraped_data["description"]
            price = scraped_data["price"]
            image_source = scraped_data["image"]

        product = form.save()
        product = get_object_or_404(Product, id=product.id)
        product.user = request.user
        product.product_link = product_link
        product.product_description = description
        product.product_picture_source = image_source
        product.product_price = price
        product.save()

        user = User.objects.filter(id=request.user.id).first()
        user.wishlisted_products['product_id'].append(product.id)
        user.save()

        messages.success(request, 'Ürün başarıyla eklendi.')
        return redirect('apps.product:dashboard')
    return render(request, 'product/add-product.html', context)


@login_required(login_url='apps.account:login')
def update_product(request, idb64):
    idb64 = force_text(urlsafe_base64_decode(idb64))

    product = get_object_or_404(Product, id=idb64)
    form = ProductForm(request.POST or None, instance=product)
    context = {
        'form': form
    }

    if form.is_valid():
        form.save()
        messages.success(request, 'Ürün başarıyla güncellendi.')
        return redirect('apps.product:dashboard')
    return render(request, 'product/update-product.html', context)


@login_required(login_url='apps.account:login')
def delete_product(request, idb64):
    idb64 = force_text(urlsafe_base64_decode(idb64))

    product = get_object_or_404(Product, id=idb64)

    user = User.objects.filter(id=request.user.id).first()
    user.wishlisted_products['product_id'].remove(product.id)
    user.save()
    product.delete()

    messages.success(request, 'Ürün başarıyla silindi.')
    return redirect('apps.product:dashboard')


@login_required(login_url='apps.account:login')
def send_product_link_to_user(request, idb64):
    idb64 = force_text(urlsafe_base64_decode(idb64))

    product = get_object_or_404(Product, id=idb64)
    context = {
        'product': product,
    }

    email_subject = 'Kaydettiğiniz Link'
    email_body = render_to_string('product/product-details.html', context)
    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_FROM_USER,
                         to=[request.user.email])
    email.send()

    messages.success(request, 'Mesaj başarıyla yollandı.')
    return redirect('apps.product:dashboard')


def scrape(product_link):
    import requests
    import time
    import random
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.61"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    # time.sleep(random.random()*3)
    html_content = session.get(f"{product_link}").text
    return html_content


def get_html_content_from_trendyol(product_link):
    result = None
    html_content = scrape(product_link)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    result = dict()
    result['description'] = soup.find(
        "h1", attrs={"class": "pr-new-br"}).get_text()
    result['price'] = soup.find("span", attrs={"class": "prc-slg"}).get_text()
    result['image'] = soup.find(
        "div", attrs={"class": "gallery-modal-content"}).find("img").get("src")
    return result


def get_html_content_from_hepsiburada(product_link):
    html_content = scrape(product_link)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    result = dict()
    result['description'] = soup.find(
        "span", attrs={"class": "product-name"}).get_text()
    result['price'] = [price.text.replace('\n', ' ').strip()
                       for price in soup.find_all('span', attrs={"id": "offering-price"})][0]
    result['image'] = soup.find(
        'img', attrs={"class": "product-image"}).get("src")
    return result


def get_favicon(page_link):
    html_content = scrape(page_link)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    if soup.find("link", attrs={"rel": "icon"}):
        favicon = soup.find("link", attrs={"rel": "icon"}).get('href')
    elif soup.find("link", attrs={"rel": "shortcut icon"}):
        favicon = soup.find("link", attrs={"rel": "shortcut icon"}).get('href')
    else:
        favicon = f'{page_link.rstrip("/")}/favicon.ico'
    return favicon

# TODO: Belli bir aralıkta işlem yapmasını sağlamalıyız. DOS saldırısı olmaması adına.


def compare_price_with_old_price(company):
    products = Product.objects.all()
    products = list(products)
    original_prices = list()
    discounted_products = list()
    for product in products:
        product.id = urlsafe_base64_encode(force_bytes(product.id))
        if urlparse(product.product_link).netloc.split('.')[1] == company.__name__.split('_')[-1]:
            result = company(product.product_link)
            scraped_price = float(result['price'].replace(
                ',', '.').split(' ')[0][:-3].replace('.', ''))
            product_price = float(product.product_price.replace(
                ',', '.').split(' ')[0][:-3].replace('.', '')) # 259,600.00 TL --> 259.600.00 TL --> 259.600.00
            if (scraped_price) != (product_price):
                update_scraped_price(product.id, result['price'])
                if (scraped_price) < (product_price):
                    original_prices.append(product_price)
                    discounted_products.append(product)
    if(len(discounted_products) != 0):
        send_discount_message(original_prices, discounted_products)


def update_scraped_price(idb64, price):
    idb64 = force_text(urlsafe_base64_decode(idb64))
    product = get_object_or_404(Product, id=idb64)
    product.product_price = price
    product.save()


def send_discount_message(original_prices, products):
    for original_price, product in zip(original_prices, products):
        idb64 = force_text(urlsafe_base64_decode(product.id))
        product = get_object_or_404(Product, id=idb64)
        context = {
            'site': 'http://127.0.0.1:8000',
            'original_price': original_price,
            'product': product,
        }

        toUserEmail = get_object_or_404(User, id=product.user_id).email

        company = urlparse(product.product_link).netloc.split('.')[1]

        email_subject = f'{company} sitesinde takip ettiğiniz {product.product_description} ürünü indirimde!'
        html_email_body = render_to_string(
            'product/product-discount.html', context)
        text_email_body = strip_tags(html_email_body)
        # TODO: Dene: https://www.youtube.com/watch?v=GdqjyAMvTE0
        email = EmailMultiAlternatives(
            email_subject, text_email_body, settings.EMAIL_FROM_USER, [toUserEmail])
        email.attach_alternative(html_email_body, "text/html")
        email.send()

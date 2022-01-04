from bs4 import BeautifulSoup
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

from selenium import webdriver


from apps.account.models import User
from .models import Product
from .forms import ProductForm

import json
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
        original_price = "0"
        discounted_price = "0"
        mean_rating = "Değerlendirme kazınamadı."
        review_count = "Yorum sayısı kazınamadı."

        if (urlparse(product_link).netloc == "www.trendyol.com"):
            scraped_data = get_html_content_from_trendyol(product_link)
            description = scraped_data["description"]
            original_price = scraped_data["original-price"]
            discounted_price = scraped_data["discounted-price"]
            image_source = scraped_data["image"]
            mean_rating = scraped_data["rating"]
            review_count = scraped_data["review-count"]

        elif (urlparse(product_link).netloc == "www.hepsiburada.com"):
            scraped_data = get_html_content_from_hepsiburada(product_link)
            description = scraped_data["description"]
            original_price = scraped_data["original-price"]
            discounted_price = scraped_data["discounted-price"]
            image_source = scraped_data["image"]
            mean_rating = scraped_data["rating"]
            review_count = scraped_data["review-count"]

        product = form.save()
        product = get_object_or_404(Product, id=product.id)
        product.user = request.user
        product.product_link = product_link
        product.product_description = description
        product.product_picture_source = image_source
        product.product_original_price = original_price
        product.product_discounted_price = discounted_price
        product.product_mean_rating = mean_rating
        product.product_review_count = review_count
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


def compare_price_with_old_price_sync(request, idb64=None):
    last_discounted_prices = list()
    discounted_products = list()
    products = list(Product.objects.all())

    if(idb64 is not None):
        idb64 = force_text(urlsafe_base64_decode(idb64))
        product = get_object_or_404(Product, id=idb64)
        products = [product]

    compare_price_with_old_price(
        get_html_content_from_hepsiburada, products, last_discounted_prices, discounted_products)
    compare_price_with_old_price(
        get_html_content_from_trendyol, products, last_discounted_prices, discounted_products)

    if(len(discounted_products) != 0):
        send_discount_message(last_discounted_prices, discounted_products)
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
    html_content = session.get(f"{product_link}").text
    # time.sleep(random.random()*3)
    return html_content


def get_html_content_from_trendyol(product_link):
    result = None
    html_content = scrape(product_link)
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')

    result = dict()
    result['description'] = soup.find(
        "h1", attrs={"class": "pr-new-br"}).get_text()

    original_price = soup.find("span",
                               attrs={"class": "prc-org"})  # None
    if(original_price is not None):
        result['original-price'] = original_price.get_text()

    result['discounted-price'] = soup.find("span",
                                           attrs={"class": "prc-slg"}).get_text()

    # Eğer orijinal fiyat yoksa, sitede indirimli fiyat alanına orijinal fiyat kaydı yapılmış dolayısıyla bu işlem gerçekleşmekte.
    # Yani indirim olmadığında orijinal fiyat alanı olarak bu id' ye ait tag kullanılmış.
    if(original_price is None):
        result['original-price'] = result['discounted-price']

    extra_discount = soup.find(
        "span", attrs={"class": "prc-dsc"})  # None
    if(extra_discount):
        result['discounted-price'] = extra_discount.get_text()

    result['image'] = soup.find(
        "div", attrs={"class": "gallery-modal-content"}).find("img").get("src")

    rating = "0"
    scripts = soup.find_all('script', type='application/javascript')
    for script in scripts:
        if 'ratingScore' in script.text:
            data = script.text.replace(
                "window.__PRODUCT_DETAIL_APP_INITIAL_STATE__=", "").split(";")[0]
            data = json.loads(data)
            rating = data["product"]["ratingScore"]["averageRating"]

    if(rating is None):
        rating = "0"

    review_count = soup.find("a", attrs={"class": "rvw-cnt-tx"})  # None
    if(review_count is None):
        review_count = soup.select_one(".pr-in-rnr-nr span").get_text()
        print(review_count)
    else:
        review_count = review_count.get_text().split(" ")[0]

    result['rating'] = rating
    result['review-count'] = review_count

    return result


def get_html_content_from_hepsiburada(product_link):
    html_content = scrape(product_link)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    result = dict()
    result['description'] = soup.find(
        "span", attrs={"class": "product-name"}).get_text()

    result['original-price'] = soup.find("del",
                                         attrs={"id": "originalPrice"}).get_text()
    result['discounted-price'] = [price.text.replace('\n', ' ').replace('\r', '').replace(
        '(Adet )', '').strip() for price in soup.find_all('span', attrs={"id": "offering-price"})][0]

    result['image'] = soup.find(
        'img', attrs={"class": "product-image"}).get("src")

    rating = soup.find("span", attrs={"class": "rating-star"})
    if(rating is not None):
        rating = rating.get_text().strip()
    else:
        rating = "0"

    review_count = soup.find("a", attrs={"class": "product-comments"})
    if(review_count is not None):
        review_count = review_count.find("span").get_text()
    else:
        review_count = soup.find(
            "span", attrs={"class": "rating-information"}).get_text()

    result["rating"] = rating
    result["review-count"] = review_count
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


def compare_price_with_old_price_async(company):
    products = Product.objects.all()
    products = list(products)
    last_discounted_prices = list()
    discounted_products = list()
    compare_price_with_old_price(
        company, products, last_discounted_prices, discounted_products)

    if(len(discounted_products) != 0):
        send_discount_message(last_discounted_prices, discounted_products)


def compare_price_with_old_price(company, products, last_discounted_prices, discounted_products):
    for product in products:
        if urlparse(product.product_link).netloc.split('.')[1] == company.__name__.split('_')[-1]:
            product.id = urlsafe_base64_encode(force_bytes(product.id))

            result = company(product.product_link)

            scraped_original_price = float(
                result['original-price'].replace(',', '.').split(' ')[0][:-3].replace('.', ''))
            scraped_discounted_price = float(
                result['discounted-price'].replace(',', '.').split(' ')[0][:-3].replace('.', ''))

            last_original_price = float(product.product_original_price.replace(
                ',', '.').split(' ')[0][:-3].replace('.', ''))
            last_discounted_price = product.product_discounted_price
            last_discounted_price_modified = float(last_discounted_price.replace(',', '.').split(
                ' ')[0][:-3].replace('.', ''))  # 259,600.00 TL --> 259.600.00 TL --> 259600.00

            if ((scraped_discounted_price != last_discounted_price_modified) or (scraped_original_price != last_original_price)):
                update_scraped_price(
                    product.id, result['original-price'], result['discounted-price'])
                if (scraped_discounted_price < last_discounted_price_modified):
                    last_discounted_prices.append(last_discounted_price)
                    discounted_products.append(product)


def update_scraped_price(idb64, original_price, discounted_price):
    idb64 = force_text(urlsafe_base64_decode(idb64))
    product = get_object_or_404(Product, id=idb64)
    product.product_original_price = original_price
    product.product_discounted_price = discounted_price
    product.save()


def send_discount_message(last_discounted_prices, products):
    for last_discounted_price, product in zip(last_discounted_prices, products):
        idb64 = force_text(urlsafe_base64_decode(product.id))
        product = get_object_or_404(Product, id=idb64)

        if(product.product_original_price == last_discounted_price):
            last_discounted_price = None

        context = {
            'last_discounted_price': last_discounted_price,
            'product': product,
        }

        user = get_object_or_404(User, id=product.user_id)

        company = urlparse(product.product_link).netloc.split('.')[1]

        email_subject = f'{company} sitesinde takip ettiğiniz {product.product_description} ürünü indirimde!'
        html_email_body = render_to_string(
            'product/product-discount.html', context)
        email = EmailMessage(subject=email_subject, body=html_email_body, from_email=settings.EMAIL_FROM_USER,
                             to=[user.email])
        email.content_subtype = 'html'
        email.send()

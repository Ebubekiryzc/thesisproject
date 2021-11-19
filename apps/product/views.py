from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail.message import EmailMessage
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
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

    for product in products:
        product.id = urlsafe_base64_encode(force_bytes(product.id))

    context = {
        'products': products
    }
    return render(request, 'product/dashboard.html', context)


@login_required(login_url='apps.account:login')
def add_product(request):
    form = ProductForm(request.POST or None)
    context = {
        'form': form
    }

    if form.is_valid():
        product = form.save()

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

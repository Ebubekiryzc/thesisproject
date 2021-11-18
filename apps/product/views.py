from django.core.mail import EmailMessage
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from apps.account.models import User
from apps.account.views import login, send_activation_email
from .models import Product
from .forms import ProductForm
from apps.account.utils import generate_token
from django.core.mail import send_mail


# Create your views here.


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
    pass


@login_required(login_url='apps.account:login')
def delete_product(request, idb64):
    pass


def send_link_email(request, user):
    current_site = get_current_site(request)
    context = {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_decode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    }


@login_required(login_url='apps.account:login')
def send_product_link_to_user(request, id):
    product = get_object_or_404(Product, id=id)
    context = {
        'product': product,
    }

    email_subject = 'Kaydettiğiniz Link'
    email_body = render_to_string('product/product-detail.html', context)
    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_FROM_USER,
                         to=[request.user.email])
    email.send()
    
    messages.success(request, 'Mesaj başarıyla yollandı.')
    return redirect('apps.product:dashboard')

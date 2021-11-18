from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.account.models import User
from apps.account.views import login
from .models import Product
from .forms import ProductForm


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
    context ={
        'form':form
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
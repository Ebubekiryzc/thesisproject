from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail.message import EmailMessage
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from apps.product.tasks import scrape_review_task

from helpers.utils import change_url_to_company_name, convert_comma_price_to_float
from .models import Product
from .forms import ProductForm


# Create your views here.
login_url = "apps.account:login"


def index(request):
    return render(request, 'product/index.html')


def about(request):
    return render(request, 'product/about.html')


@login_required(login_url=login_url)
def dashboard(request):
    current_user = request.user
    products = current_user.products_added_to_wishlist.all()

    # favicons = list()

    # TODO: Üzerinde oynama yapılacak
    # for product in products:
    #     favicons.append(get_favicon(product.product_link))

    # content = zip(products, favicons)
    content = products
    context = {
        "content": content
    }
    return render(request, 'product/dashboard.html', context)


@login_required(login_url=login_url)
def add_product(request):
    form = ProductForm(request.POST or None)
    current_user = request.user

    context = {
        'form': form
    }

    if form.is_valid():
        product = form.save(commit=False)
        product.updated_by = current_user

        # Kendi yazdığımız manager metodu ile ürün varsa ürünü yok ise NoneType referansını döndürüyoruz.
        product_occurence = Product.objects.safe_get(product.product_link)

        # Veri tabanında bu ürün var mı? Varsa bir daha kazıma işlemine girmesin boş yere.
        if product_occurence:

            # Şu an ekleyen kullanıcının istek listesine zaten eklenmiş mi?
            if current_user.products_added_to_wishlist.filter(product_link=product.product_link).exists():
                messages.warning(
                    request, 'Bu ürün zaten istek listesine eklenmiş.')
                return redirect('apps.product:dashboard')

            # Signaller şu anki kullanıcının kaydedilmesini sağlayacaktır.
            else:
                product_occurence.updated_by = current_user
                product_occurence.save()

        # Ürün henüz yeni üretilmiş bir ürünse doğrudan ekleyelim signaller gerekli işlemleri yapacaktır.
        else:
            try:
                product.save()
            except:
                messages.error(
                    request, "Bu link kazınabilecek linkler arasında bulunmamaktadır.")
                return redirect('apps.product:dashboard')

        messages.success(request, 'Ürün başarıyla eklendi.')
        return redirect('apps.product:dashboard')

    return render(request, 'product/add-product.html', context)


@login_required(login_url=login_url)
def delete_product(request, pk):

    current_user = request.user
    product = get_object_or_404(Product, id=pk)
    current_user.products_added_to_wishlist.remove(product)

    messages.success(request, 'Ürün başarıyla silindi.')
    return redirect('apps.product:dashboard')


@login_required(login_url=login_required)
def send_product_link_to_user(request, pk):
    product = get_object_or_404(Product, pk)

    context = {
        'product': product,
    }

    email_subject = 'Kaydettiğiniz Link'
    email_body = render_to_string('product/product-details.html', context)
    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_HOST_PASSWORD,
                         to=[request.user.email])
    email.send()

    messages.success(request, 'Mesaj başarıyla yollandı.')
    return redirect('apps.product:dashboard')


def check_if_product_has_new_discount(pk):
    product = get_object_or_404(Product, id=pk)

    old_discounted_price = convert_comma_price_to_float(
        product.product_discounted_price)

    product.will_be_scraped = True
    product.updated_by = None
    product.save()

    scraped_discounted_price = convert_comma_price_to_float(
        product.product_discounted_price)

    return scraped_discounted_price < old_discounted_price, old_discounted_price, product


# TODO: Burası celery task olarak yapılandırılabilir.
def send_discount_notification(old_price, current_product):
    recipients = current_product.user_set.values_list("email", flat=True)

    context = {
        'last_discounted_price': old_price,
        'product': current_product,
    }

    company = change_url_to_company_name(current_product.product_link)

    email_subject = f'{company} sitesinde takip ettiğiniz {current_product.product_description} ürünü indirimde!'
    html_email_body = render_to_string(
        'product/product-discount.html', context)
    email = EmailMessage(subject=email_subject, body=html_email_body, from_email=settings.EMAIL_HOST_PASSWORD,
                         to=recipients)
    email.content_subtype = 'html'
    email.send()


def check_if_discount_message_should_send(pk):
    new_discount, old_discounted_price, product = check_if_product_has_new_discount(
        pk)
    if new_discount:
        send_discount_notification(old_discounted_price, product)


def check_all_product_prices(products=Product.objects):
    product_ids = products.values_list("id", flat=True)
    for product_id in product_ids:
        check_if_discount_message_should_send(product_id)


@login_required(login_url=login_url)
def compare_price_for_all_products(request):
    check_all_product_prices(request.user.products_added_to_wishlist)

    messages.success(request, 'Bütün ürünler için sorgulama işlemi yapıldı.')
    return redirect('apps.product:dashboard')


@login_required(login_url=login_url)
def compare_price_for_product(request, pk):
    check_if_discount_message_should_send(pk)
    messages.success(request, 'Ürün sorgulandı.')
    return redirect('apps.product:dashboard')


@login_required(login_url=login_url)
def scrape_reviews(request, pk):
    scrape_review_task.delay(pk, request.user.id)
    messages.success(
        request, 'İstek başarıyla sıraya alındı, işlem tamamlandığında mail ile bilgilendirileceksiniz.')
    return redirect("apps.product:dashboard")

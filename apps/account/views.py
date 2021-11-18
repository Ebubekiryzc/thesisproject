from .forms import LoginForm, RegisterForm
from .models import User
from .utils import generate_token

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.shortcuts import render, redirect

from helpers.decorators import auth_user_should_not_access
# Create your views here.


@auth_user_should_not_access
def register(request):

    form = RegisterForm(request.POST or None)
    context = {
        'form': form
    }
    if form.is_valid():
        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Kullanıcı adı alınmış!')
            return render(request, 'account/register.html', context)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email adresi alınmış!')
            return render(request, 'account/register.html', context)

        newUser = User(username=username, email=email)
        newUser.set_password(password)
        newUser.save()

        send_activation_email(request, newUser)
        messages.info(request, 'Aktivasyon maili hesabınıza yollandı.')
        return redirect('apps.account:register')
    
    context = {
        'form': form
    }
    return render(request, 'account/register.html', context)


@auth_user_should_not_access
def login(request):
    form = LoginForm(request.POST or None)
    context = {
        'form': form
    }

    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Kullanıcı adı veya parola bulunamadı.')
            return render(request, 'account/login.html', context)

        if not user.is_email_verified:
            messages.error(request, 'Email adresiniz onaylanmamış.')
            return render(request, 'account/login.html', context)

        messages.success(request, 'Başarıyla giriş yapıldı.')
        auth.login(request, user)
        return redirect('index')
    
    return render(request, 'account/login.html', context)


@login_required(login_url='apps.account:login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Başarıyla çıkış yapıldı.')
    return redirect('index')


def send_activation_email(request, user):
    current_site = get_current_site(request)
    context = {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    }
    email_subject = 'Hesabınızı Aktifleştirin'
    email_body = render_to_string('account/activate.html', context)
    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.EMAIL_FROM_USER,
                         to=[user.email])
    email.send()


def activate_user(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.success(
            request, 'Email onaylama işlemi başarı ile gerçekleşti.')
        return redirect('apps.account:login')

    context = {
        "user": user
    }
    return render(request, 'account/activate-failed.html', context)

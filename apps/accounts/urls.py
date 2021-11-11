from django.conf.urls import url
from . import views

app_name = 'apps.accounts'

urlpatterns = [
    url(r'^user$', views.userApi, name='userApiWithoutParameter'),
    url(r'^user/([0-9]+)$', views.userApi, name='userApiWithParameter')
]

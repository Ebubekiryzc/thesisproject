from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'apps.account'

urlpatterns = [
    # url(r'^user$', views.userApi, name='userApiWithoutParameter'),
    # url(r'^user/([0-9]+)$', views.userApi, name='userApiWithParameter'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate_user/<uidb64>/<token>', views.activate_user, name='activate'),
]

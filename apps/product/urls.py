from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'apps.product'

urlpatterns = [
    path('dashboard/', views.dashboard ,name='dashboard'),
    path('add/', views.add_product, name='add_product'),
    path('update/<str:id>', views.update_product, name='update_product'),
    path('delete/<str:id>', views.delete_product, name='delete_product'),
    ]

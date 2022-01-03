from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'apps.product'

urlpatterns = [
    path('dashboard/', views.dashboard ,name='dashboard'),
    path('add/', views.add_product, name='add_product'),
    path('update/<str:idb64>', views.update_product, name='update_product'),
    path('delete/<str:idb64>', views.delete_product, name='delete_product'),
    path('send_mail/<str:idb64>', views.send_product_link_to_user, name='send_product_link_to_user'),
    path('comparison/', views.compare_price_with_old_price_sync, name='compare_price_with_old_price_sync'),
    path('comparison/<str:idb64>', views.compare_price_with_old_price_sync, name='compare_price_with_old_price_sync'),
    ]

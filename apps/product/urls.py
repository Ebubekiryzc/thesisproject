from django.urls import path, include
from . import views

app_name = 'apps.product'

urlpatterns = [
    path('api/', include('apps.product.api.urls')),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_product, name='add_product'),
    # path('update/<str:idb64>', views.update_product, name='update_product'),
    path('delete/<str:pk>/', views.delete_product, name='delete_product'),
    path('check_product_price/<str:pk>',
         views.compare_price_for_product, name='check_product_price'),
    path('check_all_product_prices/', views.compare_price_for_all_products,
         name='check_all_product_prices'),
    path('send_mail/<str:idb64>', views.send_product_link_to_user,
         name='send_product_link_to_user'),
    path('scrape_reviews/<str:pk>', views.scrape_reviews, name='scrape_reviews')
]

from django.urls import path, include
from apps.product.api.views import ProductAPIViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'product', ProductAPIViewSet, basename='product')


urlpatterns = [
    path('', include(router.urls)),
]

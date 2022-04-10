from django.urls import path, include
from apps.account.api.views import LoginAPIView, RegisterView, UserView, VerifyEmail
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'register', RegisterView, basename='register')
router.register(r'user', UserView, basename='user')
# router.register(r'login', LoginAPIView, basename='login')

urlpatterns = [
    path('', include(router.urls)),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('login/', LoginAPIView.as_view(), name="login"),
]

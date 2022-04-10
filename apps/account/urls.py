from django.urls import path, include
from . import views

app_name = 'apps.account'

urlpatterns = [
    path('api/', include('apps.account.api.urls')),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate_user/<uidb64>/<token>', views.activate_user, name='activate'),
]

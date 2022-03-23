


from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name = 'index'),
    path('create-account', register, name = 'register'),
    path('register_save', register_save, name = 'register_save'),
    path('login', login, name = 'login'),
    path('logout', logout, name = 'logout'),
    path('wallet', wallet, name = 'wallet'),
    path('generate_address', generate_address, name = 'generate_address'),
    path('send_coin', send_coin, name = 'send_coin'),
    path('receive_coin', receive_coin, name = 'receive_coin'),
    path('receive_coin_save', receive_coin_save, name = 'receive_coin_save'),
    path('send_coin_save', send_coin_save, name = 'send_coin_save'),
    path('history', history, name = 'history'),
    
]




urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
from django.contrib import admin
from .models import *


admin.site.register(Profile)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Notification)
admin.site.register(Receive_transaction)

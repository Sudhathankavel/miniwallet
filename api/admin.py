from django.contrib import admin
from api.models import Wallet, Customer, Transaction


# Register your models here.
admin.site.register([Wallet, Customer, Transaction])

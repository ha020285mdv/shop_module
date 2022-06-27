from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ishop.models import ShopUser, Good, Purchase, Refund

admin.site.register(ShopUser, UserAdmin)
admin.site.register(Good)
admin.site.register(Purchase)
admin.site.register(Refund)

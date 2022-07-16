from django.contrib import admin
from .models import Order
# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ('owner', 'catalogue', 'fee_amount', 'payment_status',)
    list_filter = ('owner', 'catalogue', 'payment_status',)


admin.site.register(Order, OrderAdmin)

from django.contrib import admin
from .models import Catalogue, Bid, CatalogueFile
# Register your models here.


class CatalogueAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'end_date', 'strategy', 'broker_fees')
    list_filter = ('name', 'owner', 'strategy')


class BidAdmin(admin.ModelAdmin):
    list_display = ('catalogue_name', 'bidder', 'bid_amount',)
    list_filter = ('catalogue_name', 'bidder',)


class CatalogueFileAdmin(admin.ModelAdmin):

    list_display = ('catalogue_name',)


admin.site.register(Catalogue, CatalogueAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(CatalogueFile, CatalogueFileAdmin)

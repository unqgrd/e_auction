from django.contrib import admin
from .models import Catalogue, Bid, CatalogueFile
# Register your models here.
admin.site.register(Catalogue)
admin.site.register(Bid)
admin.site.register(CatalogueFile)

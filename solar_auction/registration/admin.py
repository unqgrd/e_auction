from django.contrib import admin
from .models import UserProfileInfo, Documents
# Register your models here.


class UserProfileInfoAdmin(admin.ModelAdmin):
    list_filter = ('organization_name',)
    list_display = ('user', 'name', 'phone', 'organization_name')


class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('user',)


admin.site.register(UserProfileInfo, UserProfileInfoAdmin)
admin.site.register(Documents, DocumentsAdmin)

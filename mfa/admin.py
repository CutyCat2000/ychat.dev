from django.contrib import admin
from .models import mfaKey


class MfaKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'key')
    list_filter = ('user', )
    search_fields = ('user__username', 'key')


admin.site.register(mfaKey, MfaKeyAdmin)

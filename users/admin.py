from .models import IncompleteProfileAccessLog
from django.contrib import admin

@admin.register(IncompleteProfileAccessLog)
class IncompleteProfileAccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'attempted_path', 'timestamp', 'ip_address')
    search_fields = ('user__username', 'attempted_path')
    list_filter = ('timestamp',)

from django.contrib import admin
from .models import LogEntry,Profile


# Register your models here.

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'source', 'is_anomaly','alert_sent')
    list_filter = ('level', 'is_anomaly', 'source')
    search_fields = ('message', 'source')
    ordering = ('-timestamp',)  # 👈 Add this line
    #readonly_fields = ('timestamp', 'level', 'source', 'message', 'is_anomaly')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'admin')
    list_filter = ('role',)
    search_fields = ('user__username', 'admin__username')

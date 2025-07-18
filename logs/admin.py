from django.contrib import admin
from .models import LogEntry
# Register your models here.

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'source', 'is_anomaly')
    list_filter = ('level', 'is_anomaly', 'source')
    search_fields = ('message', 'source')


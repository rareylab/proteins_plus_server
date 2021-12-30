"""protoss admin configuration"""
from django.contrib import admin
from .models import ProtossJob


class ProtossJobAdmin(admin.ModelAdmin):
    """admin model for protoss job"""
    readonly_fields = ('date_created', 'date_last_accessed')


admin.site.register(ProtossJob, ProtossJobAdmin)

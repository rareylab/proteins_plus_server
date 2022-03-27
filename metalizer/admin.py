"""Metalizer admin configuration"""
from django.contrib import admin
from .models import MetalizerJob


class MetalizerJobAdmin(admin.ModelAdmin):
    """Admin model for Metalizer job"""
    readonly_fields = ('date_created', 'date_last_accessed')


admin.site.register(MetalizerJob, MetalizerJobAdmin)

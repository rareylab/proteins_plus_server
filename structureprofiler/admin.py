"""structureprofiler admin site configuration"""
from django.contrib import admin

from .models import StructureProfilerJob, StructureProfilerOutput


class StructureProfilerJobAdmin(admin.ModelAdmin):
    """ Admin model for Structureprofiler Job """
    readonly_fields = ('date_created', 'date_last_accessed')


admin.site.register(StructureProfilerJob, StructureProfilerJobAdmin)
admin.site.register(StructureProfilerOutput)

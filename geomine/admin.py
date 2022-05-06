"""GeoMine admin configuration"""
from django.contrib import admin
from .models import GeoMineJob, GeoMineInfo


class GeoMineJobAdmin(admin.ModelAdmin):
    """Admin model for GeoMine job"""
    readonly_fields = ('date_created', 'date_last_accessed')


admin.site.register(GeoMineJob, GeoMineJobAdmin)
admin.site.register(GeoMineInfo)


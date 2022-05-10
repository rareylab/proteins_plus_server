"""DoGSite admin configuration"""
from django.contrib import admin
from .models import DoGSiteJob, DoGSiteInfo


class DoGSiteJobAdmin(admin.ModelAdmin):
    """Admin model for DoGSite job"""
    readonly_fields = ('date_created', 'date_last_accessed')


admin.site.register(DoGSiteJob, DoGSiteJobAdmin)
admin.site.register(DoGSiteInfo)

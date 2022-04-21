"""siena admin site configuration"""

from django.contrib import admin

from .models import SienaJob, SienaInfo


class SienaAdmin(admin.ModelAdmin):
    """Siena job model for visualization on admin site"""
    readonly_fields = ('date_created', 'date_last_accessed')


admin.site.register(SienaJob, SienaAdmin)
admin.site.register(SienaInfo)

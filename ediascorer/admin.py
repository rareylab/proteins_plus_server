"""ediascorer admin site configuration"""
from django.contrib import admin

from .models import EdiaJob, AtomScores


class EdiaJobAdmin(admin.ModelAdmin):
    """Protein model for visualization on admin site"""
    readonly_fields = ('date_created', 'date_last_accessed')


admin.site.register(EdiaJob, EdiaJobAdmin)
admin.site.register(AtomScores)

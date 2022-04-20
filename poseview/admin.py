"""Admin models for Poseview"""
from django.contrib import admin
from .models import PoseviewJob


class PoseviewJobAdmin(admin.ModelAdmin):
    """Admin model for Poseview Job"""
    readonly_fields = ('date_created', 'date_last_accessed')


admin.site.register(PoseviewJob, PoseviewJobAdmin)

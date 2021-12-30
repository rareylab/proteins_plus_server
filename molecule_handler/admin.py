"""molecule_handler admin site configuration"""
from django.contrib import admin

from .models import Protein, Ligand, ElectronDensityMap, PreprocessorJob


class ProteinAdmin(admin.ModelAdmin):
    """Protein model for visualization on admin site"""
    readonly_fields = ('date_created', 'date_last_accessed')


admin.site.register(Protein, ProteinAdmin)
admin.site.register(Ligand)
admin.site.register(ElectronDensityMap)
admin.site.register(PreprocessorJob)

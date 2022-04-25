"""StructureProfiler database models"""
from django.db import models

from proteins_plus.models import ProteinsPlusJob, ProteinsPlusBaseModel
from molecule_handler.models import Protein, ElectronDensityMap, Ligand


class StructureProfilerOutput(ProteinsPlusBaseModel):
    """Django Model for storing outputdata as json strings"""
    output_data = models.JSONField()
    parent_structureprofiler_job = models.OneToOneField(
        'StructureProfilerJob', on_delete=models.CASCADE)

class StructureProfilerJob(ProteinsPlusJob):
    """Django Model for StructureProfiler job objects"""
    #inputs
    input_protein = models.ForeignKey(
        Protein, on_delete=models.CASCADE,
        related_name='child_structureprofiler_job_set')
    input_ligand = models.ForeignKey(
        Ligand, on_delete=models.CASCADE, null=True, related_name='child_structureprofiler_job_set'
    )
    electron_density_map = models.ForeignKey(
        ElectronDensityMap, on_delete=models.CASCADE, null=True,
        related_name='child_structureprofiler_job_set')
    density_file_pdb_code = models.CharField(max_length=4, null=True)

    #output
    output_data = models.OneToOneField(
        StructureProfilerOutput, on_delete=models.CASCADE, null=True)

    hash_attributes = ['input_protein', 'input_ligand', 'density_file_pdb_code', 'electron_density_map']

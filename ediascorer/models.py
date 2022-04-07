"""Ediascorer database models"""
from django.db import models

from proteins_plus.models import ProteinsPlusJob, ProteinsPlusBaseModel
from molecule_handler.models import Protein, ElectronDensityMap


class AtomScores(ProteinsPlusBaseModel):
    """Django Model for storing atom scores as json strings"""
    parent_edia_job = models.OneToOneField('EdiaJob', on_delete=models.CASCADE)
    scores = models.JSONField()


class EdiaJob(ProteinsPlusJob):
    """Django Model for Ediascorer job objects"""
    input_protein = models.ForeignKey(
        Protein, on_delete=models.CASCADE, related_name='child_edia_job_set')
    density_file_pdb_code = models.CharField(max_length=4, null=True)
    electron_density_map = models.ForeignKey(
        ElectronDensityMap, on_delete=models.CASCADE, null=True, related_name='child_edia_job_set')
    atom_scores = models.OneToOneField(AtomScores, on_delete=models.CASCADE, null=True)
    output_protein = models.OneToOneField(
        Protein, on_delete=models.CASCADE, null=True, related_name='parent_edia_job')

    hash_attributes = ['input_protein', 'density_file_pdb_code', 'electron_density_map']

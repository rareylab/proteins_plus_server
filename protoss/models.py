"""protoss database models"""
from django.db import models
from proteins_plus.models import ProteinsPlusJob
from molecule_handler.models import Protein

class ProtossJob(ProteinsPlusJob):
    """Django model for Protoss job objects"""
    input_protein = models.ForeignKey(Protein, on_delete=models.CASCADE,
                    related_name='child_protoss_job_set')
    output_protein = models.OneToOneField(Protein, on_delete=models.CASCADE,
                    null=True, related_name='parent_protoss_job')

    hash_attributes = ['input_protein']

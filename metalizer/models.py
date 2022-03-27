"""Metalizer models"""
from django.db import models
from proteins_plus.models import ProteinsPlusJob
from molecule_handler.models import Protein


class MetalizerJob(ProteinsPlusJob):
    """Metalizer job model"""
    # inputs
    input_protein = models.ForeignKey(
        Protein, on_delete=models.CASCADE, related_name='child_metalizer_job_set')
    residue_id = models.IntegerField()
    chain_id = models.CharField(max_length=2)
    name = models.CharField(max_length=2)
    distance_threshold = models.FloatField()
    # outputs
    output_protein = models.ForeignKey(
        Protein, on_delete=models.CASCADE, related_name='parent_metalizer_job', null=True)
    metalizer_result = models.JSONField(null=True)

    # hash all inputs
    hash_attributes = ['input_protein', 'residue_id', 'chain_id', 'name', 'distance_threshold']

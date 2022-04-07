"""Metalizer models"""
from django.db import models
from proteins_plus.models import ProteinsPlusJob, ProteinsPlusBaseModel
from molecule_handler.models import Protein


class MetalizerInfo(ProteinsPlusBaseModel):
    """Metalizer info model

    Contains information about metal coordination.
    """
    parent_metalizer_job = models.OneToOneField('MetalizerJob', on_delete=models.CASCADE)
    info = models.JSONField()


class MetalizerJob(ProteinsPlusJob):
    """Metalizer job model"""
    # inputs
    input_protein = models.ForeignKey(
        Protein, on_delete=models.CASCADE, related_name='child_metalizer_job_set')
    residue_id = models.CharField(max_length=4)
    chain_id = models.CharField(max_length=2)
    name = models.CharField(max_length=2)
    distance_threshold = models.FloatField()
    # outputs
    output_protein = models.OneToOneField(
        Protein, on_delete=models.CASCADE, related_name='parent_metalizer_job', null=True)
    metalizer_info = models.OneToOneField(MetalizerInfo, on_delete=models.CASCADE, null=True)

    # hash all inputs
    hash_attributes = ['input_protein', 'residue_id', 'chain_id', 'name', 'distance_threshold']

"""GeoMine models"""
from django.db import models
from proteins_plus.models import ProteinsPlusJob, ProteinsPlusBaseModel


class GeoMineInfo(ProteinsPlusBaseModel):
    """GeoMine info model

    Contains information about matched proteins, pockets and geometric patterns.
    """
    parent_geomine_job = models.OneToOneField('GeoMineJob', on_delete=models.CASCADE)
    info = models.JSONField()


class GeoMineJob(ProteinsPlusJob):
    """GeoMine job model"""
    # inputs
    filter_file = models.CharField(max_length=256)
    # outputs
    geomine_result = models.JSONField(null=True)
    geomine_info = models.OneToOneField(GeoMineInfo, on_delete=models.CASCADE, null=True)
    # hash all inputs
    hash_attributes = ['filter_file']

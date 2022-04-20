"""Poseview models"""
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from proteins_plus.models import ProteinsPlusJob
from molecule_handler.models import Protein, Ligand


class PoseviewJob(ProteinsPlusJob):
    """Poseview job model"""
    # inputs
    input_protein = models.ForeignKey(
        Protein, on_delete=models.CASCADE, related_name='child_poseview_job_set')
    input_ligand = models.ForeignKey(
        Ligand, on_delete=models.CASCADE, related_name='child_poseview_job_set')
    # output
    image = models.ImageField(
        upload_to=settings.MEDIA_DIRECTORIES['posview_images'], blank=True, null=True)

    # hash both inputs
    hash_attributes = ['input_protein', 'input_ligand']


@receiver(pre_delete, sender=PoseviewJob)
def poseview_image_delete(sender, instance, **_kwargs):  # pylint: disable=unused-argument
    """Make sure Poseview image is deleted on job deletion

    :param sender: sender of the deletion signal, not used
    :type instance: PoseviewJob
    :param instance: Poseview job instance
    :type instance: PoseviewJob
    """
    instance.image.delete(False)

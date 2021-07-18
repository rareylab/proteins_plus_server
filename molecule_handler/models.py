"""molecule_handler database models"""
from tempfile import NamedTemporaryFile
from contextlib import nullcontext

from django.db import models
# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.conf import settings

from proteins_plus.common import ProteinsPlusJob

class Protein(models.Model):
    """Django model for Protein objects"""
    name = models.CharField(max_length=255)
    pdb_code = models.CharField(max_length=4, null=True)
    uniprot_code = models.CharField(max_length=10, null=True)
    file_type = models.CharField(max_length=3, default='pdb')
    file_string = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_accessed = models.DateTimeField(auto_now=True)

    def write_temp(self):
        """Write content of file_string to a temporary file

        :return: temporary protein file
        :rtype: NamedTemporaryFile
        """
        temp_file = NamedTemporaryFile(mode='w+', suffix='.pdb')
        temp_file.write(self.file_string)
        temp_file.seek(0)
        return temp_file

    def write_ligands_temp(self):
        """Write all corresponding ligands to one temporary multi-sdf file

        :return: temporary multi sdf file or None, if no Ligand objects are associated
        :rtype: NamedTemporaryFile or None
        """
        if self.ligand_set.count() == 0:
            return nullcontext(None)

        temp_file = NamedTemporaryFile(mode='w+', suffix='.sdf')
        for ligand in self.ligand_set.all():
            temp_file.write(ligand.file_string)
        temp_file.seek(0)
        return temp_file

class Ligand(models.Model):
    """Django model for Ligand objects. Always associated with a Protein object"""
    protein = models.ForeignKey(Protein, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=3, default='sdf')
    file_string = models.TextField()
    image = models.ImageField(upload_to=settings.MEDIA_DIRECTORIES['ligands'],
                            blank=True, null=True)

class ElectronDensityMap(models.Model):
    """Django Model for electron density map files"""
    file = models.FileField(upload_to=settings.MEDIA_DIRECTORIES['density_files'])

class PreprocessorJob(ProteinsPlusJob):
    """Django model for Preprocessor job objects"""
    protein_name = models.CharField(max_length=255)
    pdb_code = models.CharField(max_length=4, null=True)
    uniprot_code = models.CharField(max_length=10, null=True)
    protein_string = models.TextField(null=True)
    protein_file_type = models.CharField(max_length=3, default='pdb')
    ligand_string = models.TextField(null=True)
    ligand_file_type = models.CharField(max_length=3, default='sdf')
    output_protein = models.OneToOneField(Protein, on_delete=models.CASCADE,
                    null=True, related_name='parent_preprocessor_job')

@receiver(pre_delete, sender=Ligand)
def ligand_image_delete(sender, instance, **kwargs): # pylint: disable=unused-argument
    """Make sure corresponding image is deleted when Ligand object is deleted

    :param sender: sender of deletion signal. Not in use
    :param instance: Ligand object to be deleted
    :type instance: Ligand
    """
    instance.image.delete(False)

@receiver(pre_delete, sender=ElectronDensityMap)
def electrondensitymap_file_delete(sender, instance, **kwargs): # pylint: disable=unused-argument
    """Make sure corresponding density file is deleted when ElectronDensityMap object
        is deleted

    :param sender: sender of deletion signal. Not in use
    :param instance: ElectronDensityMap object to be deleted
    :type instance: ElectronDensityMap
    """
    instance.file.delete(False)

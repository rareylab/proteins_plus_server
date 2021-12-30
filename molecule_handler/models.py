"""molecule_handler database models"""
import os
from tempfile import NamedTemporaryFile
from contextlib import nullcontext

from django.db import models
# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.conf import settings

from proteins_plus.models import ProteinsPlusJob, ProteinsPlusHashableModel


class Protein(ProteinsPlusHashableModel):
    """Django model for Protein objects"""
    name = models.CharField(max_length=255)
    pdb_code = models.CharField(max_length=4, null=True)
    uniprot_code = models.CharField(max_length=10, null=True)
    file_type = models.CharField(max_length=3, default='pdb')
    file_string = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_accessed = models.DateTimeField(auto_now=True)

    hash_attributes = ['pdb_code', 'uniprot_code', 'file_type', 'file_string']

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


class Ligand(ProteinsPlusHashableModel):
    """Django model for Ligand objects. Always associated with a Protein object"""
    protein = models.ForeignKey(Protein, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=3, default='sdf')
    file_string = models.TextField()
    image = models.ImageField(upload_to=settings.MEDIA_DIRECTORIES['ligands'],
                              blank=True, null=True)

    hash_attributes = ['protein', 'file_type', 'file_string']


class ElectronDensityMap(ProteinsPlusHashableModel):
    """Django Model for electron density map files"""
    file = models.FileField(upload_to=settings.MEDIA_DIRECTORIES['density_files'])

    hash_attributes = ['file']


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

    hash_attributes = ['pdb_code', 'uniprot_code',
                       'protein_string', 'protein_file_type',
                       'ligand_string', 'ligand_file_type']

    @staticmethod
    def from_file(protein_file, ligand_file=None):
        """Build a PreprocessorJob from file(s)

        :param protein_file: Protein file to build job from
        :param ligand_file: Optional ligand file to build job from
        """
        protein_string = protein_file.file.read().decode('utf8')
        protein_name = os.path.basename(protein_file.name)
        protein_name = os.path.splitext(protein_name)[0]
        ligand_string = None
        if ligand_file:
            ligand_string = ligand_file.file.read().decode('utf8')
        return PreprocessorJob(
            protein_name=protein_name,
            protein_string=protein_string,
            ligand_string=ligand_string
        )


@receiver(pre_delete, sender=Ligand)
def ligand_image_delete(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Make sure corresponding image is deleted when Ligand object is deleted

    :param sender: sender of deletion signal. Not in use
    :param instance: Ligand object to be deleted
    :type instance: Ligand
    """
    instance.image.delete(False)


@receiver(pre_delete, sender=ElectronDensityMap)
def electrondensitymap_file_delete(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Make sure corresponding density file is deleted when ElectronDensityMap object
        is deleted

    :param sender: sender of deletion signal. Not in use
    :param instance: ElectronDensityMap object to be deleted
    :type instance: ElectronDensityMap
    """
    instance.file.delete(False)

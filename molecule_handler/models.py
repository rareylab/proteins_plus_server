"""molecule_handler database models"""
import os
import requests
from tempfile import NamedTemporaryFile, TemporaryFile
from contextlib import nullcontext

from django.core.files import File
from django.db import models

# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.conf import settings

from proteins_plus.models import ProteinsPlusJob, ProteinsPlusHashableModel
from .protein_site_handler import ProteinSiteHandler


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

    @staticmethod
    def from_file(protein_file, pdb_code=None, uniprot_code=None, file_type='pdb'):
        """Build a protein from a file"""
        protein_string = protein_file.read()
        if isinstance(protein_string, bytes):
            protein_string = protein_string.decode('utf8')

        if pdb_code:
            protein_name = pdb_code
        else:
            protein_name = os.path.basename(protein_file.name)
            protein_name = os.path.splitext(protein_name)[0]
        return Protein(
            name=protein_name,
            pdb_code=pdb_code,
            uniprot_code=uniprot_code,
            file_type=file_type,
            file_string=protein_string
        )

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
            return None

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

    @staticmethod
    def from_file(ligand_file, protein, file_type='sdf', image=None):
        """Build a ligand from a file"""
        ligand_string = ligand_file.read()
        if isinstance(ligand_string, bytes):
            ligand_string = ligand_string.decode('utf8')
        ligand_name = os.path.basename(ligand_file.name)
        ligand_name = os.path.splitext(ligand_name)[0]
        return Ligand(
            name=ligand_name,
            file_string=ligand_string,
            file_type=file_type,
            protein=protein,
            image=image
        )

    def write_temp(self):
        """Write content of file_string to a temporary file

        :return: temporary ligand file
        :rtype: NamedTemporaryFile
        """
        temp_file = NamedTemporaryFile(mode='w+', suffix='.' + self.file_type)
        temp_file.write(self.file_string)
        temp_file.seek(0)
        return temp_file


class ProteinSite(ProteinsPlusHashableModel):
    """Django model for ProteinSite objects.

    Always associated with a Protein object. This model describes a part of a protein
    structure. It is used to represent a binding sites, protein-protein interfaces (PPIs),
    residue 3D micro-environments and more.

    The site_description looks like this:
        {'residue_ids': [
            {'name': 'LEU', 'position': '145', 'chain': 'A'},
            {'name': 'TRP', 'position': '146', 'chain': 'A'},
        ]}
    """
    protein = models.ForeignKey(Protein, on_delete=models.CASCADE, blank=True, null=True)
    site_description = models.JSONField()

    hash_attributes = ['protein', 'site_description']

    @staticmethod
    def from_edf(protein, edf_path):
        """Convenience function to create a ProteinSite from EDF file for the given Protein.

        note:: Reference protein path in EDF file will be ignored. Instead protein will
              set as reference.
        :param protein: The protein for which the site in the EDF file belongs.
        :type protein: Protein
        :param edf_path: File path to EDF file.
        :type edf_path: pathlib.Path
        :return: A new ProteinSite.
        :rtype: ProteinSite
        """
        return ProteinSite(
            protein=protein,
            site_description=ProteinSiteHandler.edf_to_json(edf_path))

    def write_edf_temp(self, protein_filepath):
        """Write site as EDF (ensemble data file, a NAOMI intern file format) to a temporary file

        :param Filepath to the parent Protein.
        :return: temporary EDF file
        :rtype: NamedTemporaryFile
        """
        temp_file = NamedTemporaryFile(mode='w+', suffix='.edf')
        temp_file.write(ProteinSiteHandler.proteinsite_to_edf(self, protein_filepath))
        temp_file.seek(0)
        return temp_file


class ElectronDensityMap(ProteinsPlusHashableModel):
    """Django Model for electron density map files"""
    file = models.FileField(upload_to=settings.MEDIA_DIRECTORIES['density_files'])
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_accessed = models.DateTimeField(auto_now=True)

    hash_attributes = ['file']

    @staticmethod
    def from_ccp4(ccp4_path):
        """Convenience function to create an ElectronDensityMap from CCP4 file.

        :param ccp4_path: File path to CCP4 file.
        :type ccp4_path: pathlib.Path
        :return: A new ElectronDensityMap.
        :rtype: ElectronDensityMap
        """
        density_map = ElectronDensityMap()
        with ccp4_path.open(mode='rb') as density_file:
            density_file_container = File(density_file, name=ccp4_path.name)
            density_map.file.save(ccp4_path.name, density_file_container)
        return density_map

    @staticmethod
    def from_pdb_code(pdb_code):
        """Fetch electron density file from server and save it in an ElectronDensityMap instance

        :param pdb_code: pdb code of protein in question
        :type pdb_code: str
        :return: A new ElectronDensityMap
        :rtype: ElectronDensityMap instance or NONE if failure
        """

        url = f'{settings.URLS["density_files"]}{pdb_code}.ccp4'
        req = requests.get(url)
        if req.status_code != 200:
            return None
        density_map = ElectronDensityMap()
        with TemporaryFile() as tmpfile:
            content_as_bytes = bytearray(req.content)
            tmpfile.write(content_as_bytes)
            tmpfile.seek(0)
            density_map.file.save(f'{pdb_code}.ccp4', File(tmpfile))
            density_map.save()

        return density_map


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

"""SIENA database models"""
from django.db import models

from proteins_plus.models import ProteinsPlusJob, ProteinsPlusBaseModel
from molecule_handler.models import Ligand, Protein, ProteinSite


class SienaInfo(ProteinsPlusBaseModel):
    """Siena info model

    Contains information about result statistics and binding site alignments.
    """
    parent_siena_job = models.OneToOneField('SienaJob', on_delete=models.CASCADE)
    # holds the SIENA resultStatistic.csv as a JSON dict
    statistic = models.JSONField()
    # holds the SIENA alignment.txt file as a file_string
    alignment = models.TextField()


class SienaJob(ProteinsPlusJob):
    """Django Model for SIENA job objects"""
    input_protein = models.ForeignKey(
        Protein, on_delete=models.CASCADE, related_name='child_siena_job_set')
    input_ligand = models.ForeignKey(Ligand, on_delete=models.CASCADE, null=True,
                                     related_name='child_siena_job_set')
    input_site = models.ForeignKey(ProteinSite, on_delete=models.CASCADE, null=True,
                                   related_name='child_siena_job_set')
    # holds info on SIENA results
    output_info = models.OneToOneField(SienaInfo, on_delete=models.CASCADE, null=True)
    # holds the SIENA ensemble protein structures that are superposed on the input protein.
    # Ligands of this ensemble are associated with the ensemble proteins.
    output_proteins = models.ManyToManyField(Protein, related_name='parent_siena_job')

    hash_attributes = ['input_protein', 'input_ligand', 'input_site']

    def get_ensemble_ligands(self):
        """Retrieve ensemble ligands from SIENA search.

        Ligands determined by SIENA to be in the protein hits binding pockets are returned.
        The ligands are returned with their associated protein model.
        Note that protein hits without a ligand in the binding site are omitted by this
        function.
        :return: All ligands of the binding site ensemble determined by SIENA.
        :rtype: generator yielding tuples
        """
        for protein in self.output_proteins.all():
            for ligand in Ligand.objects.filter(protein=protein):
                yield ligand, protein

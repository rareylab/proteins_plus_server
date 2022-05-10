"""DoGSite models"""
from django.db import models
from proteins_plus.models import ProteinsPlusJob, ProteinsPlusBaseModel
from molecule_handler.models import ElectronDensityMap, Ligand, Protein, ProteinSite


class DoGSiteInfo(ProteinsPlusBaseModel):
    """DoGSite info model

    Contains information about pocket statistics.
    """
    parent_dogsite_job = models.OneToOneField('DoGSiteJob', on_delete=models.CASCADE)
    # holds the DoGSite desc.txt as a JSON dict
    info = models.JSONField()


class DoGSiteJob(ProteinsPlusJob):
    """DoGSite job model"""
    input_protein = models.ForeignKey(
        Protein, on_delete=models.CASCADE, related_name='child_dogsite_job_set')
    input_ligand = models.ForeignKey(Ligand, on_delete=models.CASCADE, null=True,
                                     related_name='child_dogsite_job_set')
    # can be used to limit pocket detection to a chain
    chain_id = models.CharField(max_length=2, default='')
    # can be pocket or subpocket
    calc_subpockets = models.BooleanField(default=False)
    # use ligand position to annotate grid and make pocket detection easier at these positions
    ligand_bias = models.BooleanField(default=False)
    # output protein pockets
    output_pockets = models.ManyToManyField(ProteinSite, related_name='parent_dogsite_job')
    # output density files
    output_densities = models.ManyToManyField(ElectronDensityMap, related_name='parent_dogsite_job')
    # holds info about pocket statistics
    dogsite_info = models.OneToOneField(DoGSiteInfo, on_delete=models.CASCADE, null=True)

    # hash all inputs
    hash_attributes = ['input_protein', 'input_ligand', 'chain_id', 'calc_subpockets',
                       'ligand_bias']

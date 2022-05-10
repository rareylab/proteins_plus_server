"""Helper functions for the DoGSite unit tests"""
from molecule_handler.test.utils import create_test_protein, create_test_ligand, \
    create_test_proteinsite, create_test_electrondensitymap
from ..models import DoGSiteJob, DoGSiteInfo
from .config import TestConfig


def create_test_dogsite_job(
        ligand_name=TestConfig.ligand,
        chain_id=TestConfig.chain_id,
        calc_subpockets=TestConfig.calc_subpockets,
        ligand_bias=TestConfig.ligand_bias):
    """Helper function for creating dummy DoGSiteJob objects

    :param ligand_name: Optional ligand name
    :type ligand_name: str
    :param chain_id: Optional chain id
    :type chain_id: char
    :param calc_subpockets: Optional boolean to calculate subpockets if set to true
    :type calc_subpockets: bool
    :param ligand_bias: Optional boolean to use ligand bias if set to true
    :type ligand_bias: bool
    :return: dummy DoGSiteJob object
    :rtype: DoGSiteJob
    """
    input_protein = create_test_protein(TestConfig.protein)
    input_ligand = None
    if ligand_name:
        input_ligand = create_test_ligand(input_protein, ligand_name=ligand_name)

    job = DoGSiteJob(
        input_protein=input_protein,
        input_ligand=input_ligand,
        chain_id=chain_id,
        calc_subpockets=calc_subpockets,
        ligand_bias=ligand_bias
    )
    job.save()
    return job


def create_successful_dogsite_job():
    """Helper function for creating dummy successful DoGSiteJob objects

    :return: dummy DoGSiteJob object
    :rtype: DoGSiteJob
    """
    job = create_test_dogsite_job()
    protein = create_test_protein(protein_name=TestConfig.protein,
                                  protein_filepath=TestConfig.protein_file,
                                  pdb_code=TestConfig.protein)
    output_pockets = create_test_proteinsite(protein)
    output_pockets.save()
    job.output_pockets.add(output_pockets)
    output_densities = create_test_electrondensitymap()
    output_densities.save()
    job.output_densities.add(output_densities)
    dogsite_info = DoGSiteInfo(parent_dogsite_job=job, info={"col1": "val1"})
    dogsite_info.save()
    job.dogsite_info = dogsite_info
    job.save()
    return job

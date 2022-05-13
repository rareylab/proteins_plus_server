"""Helper functions for the ediascorer unit tests"""
from django.core.files import File

from molecule_handler.models import ElectronDensityMap
from molecule_handler.test.utils import create_test_protein

from ..models import EdiaJob, EdiaScores
from .config import TestConfig


def create_test_edia_job(
        pdb_code=TestConfig.protein,
        density_filepath=TestConfig.density_file):
    """Helper function for creating dummy EdiaJob objects

    :param pdb_code: pdb code for the EdiaJob, defaults to TestConfig.protein
    :type pdb_code: str, optional
    :param density_filepath: Path to an electron density file, defaults to TestConfig.density_file
    :type density_filepath: Path, optional
    :return: Dummy EdiaJob object
    :rtype: EdiaJob
    """
    protein = create_test_protein(pdb_code=pdb_code)
    edia_job = EdiaJob(
        input_protein=protein,
        density_file_pdb_code=pdb_code
    )
    edia_job.save()

    if density_filepath is not None:
        density_map = ElectronDensityMap()
        with open(density_filepath, 'rb') as density_file:
            density_map.file.save(
                'density_map', File(density_file)
            )
        density_map.save()

        edia_job.electron_density_map = density_map
        edia_job.save()

    return edia_job


def create_successful_edia_job(
        pdb_code=TestConfig.protein,
        density_filepath=TestConfig.density_file,
        atom_scores=TestConfig.atom_scores_file):
    """Helper function for creating dummy successful EdiaJob objects

    :param pdb_code: pdb code for the EdiaJob, defaults to TestConfig.protein
    :type pdb_code: str, optional
    :param density_filepath: Path to an electron density file, defaults to TestConfig.density_file
    :type density_filepath: Path, optional
    :param atom_scores: file path to a JSON of atom scores, defaults to TestConfig.atom_scores_file
    :type atom_scores: str, optional
    :return: Dummy EdiaJob object
    :rtype: EdiaJob
    """
    job = create_test_edia_job(pdb_code=pdb_code, density_filepath=density_filepath)
    output_protein = create_test_protein(pdb_code=pdb_code)
    job.output_protein = output_protein
    with open(atom_scores) as atom_scores_file:
        edia_scores = EdiaScores(structure_scores=dict(), atom_scores=atom_scores_file.read(), parent_edia_job=job)
    edia_scores.save()
    job.edia_scores = edia_scores
    job.save()
    return job

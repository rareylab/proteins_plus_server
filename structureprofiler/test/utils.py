"""Helper functions for the structureprofiler unit tests"""
from django.core.files import File

from molecule_handler.models import ElectronDensityMap
from molecule_handler.test.utils import create_test_protein

from ..models import StructureProfilerJob, StructureProfilerOutput
from .config import TestConfig


def create_test_structureprofiler_job(
        pdb_code=TestConfig.protein,
        density_file_path=TestConfig.density_file, ligand_path=None):
    """Helper function for creating dummy Structureprofiler objects

    :param pdb_code: pdb code for the Structureprofiler defaults to TestConfig.protein
    :type pdb_code: str, optional
    :param density_file_path: Path to an electron density file, defaults to TestConfig.density_file
    :type density_file_path: Path, optional
    :param ligand_path: Path to a ligand file, defaults to None
    :type: Path, optional
    :return: Dummy StructureProfiler object
    :rtype: StructureProfiler
    """
    protein = create_test_protein(pdb_code=pdb_code)

    structureprofiler_job = StructureProfilerJob(
        input_protein=protein,
        density_file_pdb_code=pdb_code,
        input_ligand=ligand_path
    )
    structureprofiler_job.save()

    if density_file_path is not None:
        density_map = ElectronDensityMap()
        filename = density_file_path.name

        with open(density_file_path, 'rb') as density_file:
            density_map.file.save(
                filename, File(density_file)
            )
        density_map.save()
        structureprofiler_job.electron_density_map = density_map
        structureprofiler_job.save()

    return structureprofiler_job

def create_successful_structureprofiler_job(pdb_code=TestConfig.protein,
        density_file_path=TestConfig.density_file,
        output_data=TestConfig.output_file):
    """Helper function for creating dummy successful Structureprofiler objects

        :param pdb_code: pdb code for the StructureprofilerJob, defaults to TestConfig.protein
        :type pdb_code: str, optional
        :param density_file_path: Path to an electron density file, defaults to TestConfig.density_file
        :type density_file_path: Path, optional
        :param output_data: file path to a JSON of output_data, defaults to TestConfig.output_file
        :type output_data: str, optional
        :return: Dummy StructureProfilerJob object
        :rtype: StructureProfilerJob
        """
    job = create_test_structureprofiler_job(
        pdb_code=pdb_code, density_file_path=density_file_path)
    with open(output_data) as output_file:
        output_data = StructureProfilerOutput(
            output_data=output_file.read(), parent_structureprofiler_job=job)
    output_data.save()
    job.output_data = output_data
    job.save()
    return job

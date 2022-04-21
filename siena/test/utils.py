"""Helper functions for the siena unit tests"""
from pathlib import Path
from tempfile import TemporaryDirectory

from molecule_handler.test.utils import create_test_protein, create_test_ligand, \
    create_test_proteinsite

from siena.generate_siena_database_wrapper import GenerateSienaDatabaseWrapper
from ..models import SienaJob, SienaInfo
from .config import TestConfig


def create_test_siena_job(
        pdb_code=TestConfig.protein_4agm,
        protein_filepath=TestConfig.protein_file_4agm,
        ligand=TestConfig.ligand_4agm,
        site=None):
    """Helper function for creating dummy SienaJob objects

    :param pdb_code: PDB code
    :type pdb_code: str
    :param protein_filepath: path to PDB file
    :type protein_filepath: pathlib.Path
    :param ligand: Optional ligand name
    :type ligand: str
    :param site: Optional path to site definition dict
    :type site: dict
    :return: A new SienaJob with input parameters set, ready for execution.
    """
    protein = create_test_protein(protein_name=pdb_code, protein_filepath=protein_filepath,
                                  pdb_code=pdb_code)
    siena_job = None
    if site is not None:
        test_site = create_test_proteinsite(protein, site_json_dict=site)
        siena_job = SienaJob(
            input_protein=protein,
            input_site=test_site,
        )
    elif ligand is not None:
        test_ligand = create_test_ligand(protein, ligand_name=ligand)
        siena_job = SienaJob(
            input_protein=protein,
            input_ligand=test_ligand,
        )
    else:
        raise AssertionError('Wrong use of function. Provide site or ligand.')
    return siena_job


def create_successful_siena_job(use_site=False):
    """Creates a dummy SienaJob object with input and output.

    :param use_site: Whether to use site or ligand as input.
    :type use_site: bool
    :return: A new dummy SienaJob with input and output set.
    """
    if use_site:
        job = create_test_siena_job(site=TestConfig.site_json_4agm)
    else:
        job = create_test_siena_job()
    output_protein = create_test_protein(TestConfig.protein_4agm)
    output_protein.save()
    output_ligand = create_test_ligand(output_protein)
    output_ligand.save()
    job.output_proteins.add(output_protein)
    siena_info = SienaInfo(parent_siena_job=job, statistic={"col1": "val1"},
                           alignment="Alignment")
    siena_info.save()
    job.output_info = siena_info
    job.save()
    return job


def create_generate_siena_database_source_dir(destination_directory, protein_file_paths):
    """Creates symlinks in destination_dir to all files in protein_file_paths

    :param destination_directory: The destination directory
    :type destination_directory: pathlib.Path
    :param protein_file_paths: List of protein file paths.
    :type protein_file_paths: list
    """
    for path in protein_file_paths:
        (destination_directory / path.name).symlink_to(path.resolve())


class TmpSienaDB:
    """Handles lifetime of a temporary SIENA database"""
    def __init__(self, protein_file_paths, compressed=False):
        """
        Generate a temporary SIENA search DB from the provided protein files.

        :param protein_file_paths: List of protein file paths.
        :type protein_file_paths: list
        :param compressed: Whether protein files are compressed.
        :type compressed: bool
        """
        self.directory = TemporaryDirectory()
        dir_path = Path(self.directory.name)

        pdb_data_dir = dir_path / 'pdb_data'
        pdb_data_dir.mkdir()
        create_generate_siena_database_source_dir(
            destination_directory=pdb_data_dir,
            protein_file_paths=protein_file_paths
        )

        self.database_file = dir_path / 'siena.db'
        GenerateSienaDatabaseWrapper.execute_generate_siena_database(
            database_filename=self.database_file.name,
            source_dir=pdb_data_dir,
            destination_dir=dir_path,
            compressed=compressed,
        )

    def get_siena_db(self):
        """
        Get SIENA database file path.
        :return: SIENA database file path.
        :rtype: pathlib.Path
        """
        return self.database_file

    def close(self):
        """
        Close the temporary SIENA database and it's containing directory.
        """
        self.directory.cleanup()

    def __enter__(self):
        """
        ContextManager enter function. Returns SIENA database path.
        :return: SIENA database file path.
        :rtype: pathlib.Path
        """
        return self.get_siena_db()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit function. Closes the temporary SIENA database and it's directory.
        :param exc_type: ContextManager type
        :param exc_val: ContextManager value
        :param exc_tb: ContextManager traceback
        """
        self.close()

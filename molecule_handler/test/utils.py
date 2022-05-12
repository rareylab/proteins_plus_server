"""Helper functions for the molecule_handler unit tests"""
from tempfile import TemporaryFile
from django.core.files import File
from proteins_plus.models import Status
from ..models import Protein, Ligand, PreprocessorJob, ProteinSite, ElectronDensityMap
from .config import TestConfig


def create_test_preprocessor_job(ligand_filepath=TestConfig.ligand_file):
    """Helper function for creating dummy PreprocessorJob objects

    :param ligand_filepath: Path to an sdf file that will be used as input to the PreprocessorJob
                        object, defaults to TestConfig.ligand_file
    :type ligand_filepath: Path, optional
    :return: Dummy PreprocessorJob object
    :rtype: PreprocessorJob
    """
    with open(TestConfig.protein_file) as protein_file:
        protein_string = protein_file.read()
    job = PreprocessorJob(
        protein_name=TestConfig.protein,
        pdb_code=TestConfig.protein,
        protein_string=protein_string,
    )

    if ligand_filepath is not None:
        with open(ligand_filepath) as ligand_file:
            ligand_string = ligand_file.read()
        job.ligand_string = ligand_string

    job.save()
    return job


def create_successful_preprocessor_job():
    """Helper function for creating dummy successful PreprocessorJob objects

    :return: Dummy PreprocessorJob object
    :rtype: PreprocessorJob
    """
    preprocessor_job = create_test_preprocessor_job()
    output_protein = create_test_protein()
    create_test_ligand(output_protein)
    preprocessor_job.output_protein = output_protein
    preprocessor_job.status = Status.SUCCESS
    preprocessor_job.save()
    return preprocessor_job


def create_test_protein(protein_name=TestConfig.protein,
                        protein_filepath=TestConfig.protein_file,
                        pdb_code=TestConfig.protein,
                        empty=False):
    """Helper function for creating dummy Protein objects

    :param protein_name: Name of the dummy Protein object, defaults to TestConfig.protein
    :type protein_name: str, optional
    :param protein_filepath: Path to a pdb file, defaults to TestConfig.protein_file
    :type protein_filepath: Path, optional
    :param pdb_code: pdb code for the dummy Protein object, defaults to TestConfig.protein
    :type pdb_code: str, optional
    :param empty: Boolean deciding whether the dummy Protein object should be created without pdb
                    file input, defaults to False
    :type empty: bool, optional
    :return: Dummy Protein object
    :rtype: Protein
    """
    protein_string = ''
    if not empty:
        with open(protein_filepath) as protein_file:
            protein_string = protein_file.read()
    protein = Protein(
        name=protein_name, file_type='pdb', pdb_code=pdb_code, file_string=protein_string)
    protein.save()
    return protein


def create_test_ligand(protein, ligand_name=TestConfig.ligand,
                       ligand_filepath=TestConfig.ligand_file):
    """Helper function for creating dummy Ligand objects

    :param protein: Protein object that the created dummy Ligand object should be associated with
    :type protein: Protein
    :param ligand_name: Name of the dummy Ligand object, defaults to TestConfig.ligand
    :type ligand_name: str, optional
    :param ligand_filepath: Path to an sdf file, defaults to TestConfig.ligand_file
    :type ligand_filepath: Path, optional
    :return: Dummy Ligand object
    :rtype: Ligand
    """
    with open(ligand_filepath) as ligand_file:
        ligand_string = ligand_file.read()
    ligand = Ligand(
        name=ligand_name, file_type='sdf', file_string=ligand_string, protein=protein)
    ligand.save()
    return ligand


def create_multiple_test_ligands(
        protein,
        ligand=TestConfig.ligand,
        ligand2=TestConfig.ligand2,
        ligand_file1=TestConfig.ligand_file,
        ligand_file2=TestConfig.ligand2_file):
    """Helper function for creating two dummy ligand objects

    :param protein: Protein object that the created dummy Ligand object should be associated with
    :type protein: Protein
    :param ligand: Name of the first dummy Ligand object, defaults to TestConfig.ligand
    :type ligand: str, optional
    :param ligand2: Name of the second dummy Ligand object, defaults to TestConfig.ligand2
    :type ligand2: str, optional
    :param ligand_file1: Path to an sdf file for the first dummy Ligand object,
                        defaults to TestConfig.ligand_file
    :type ligand_file1: Path, optional
    :param ligand_file2: Path to an sdf file for the second dummy Ligand object,
                        defaults to TestConfig.ligand_file
    :type ligand_file1: Path, optional
    :return: Two dummy Ligand objects
    :rtype: Tuple(Ligand, Ligand)
    """
    ligand1 = create_test_ligand(protein, ligand, ligand_file1)
    ligand2 = create_test_ligand(protein, ligand2, ligand_file2)
    return ligand1, ligand2


def create_test_proteinsite(protein, site_json_dict=None):
    """Helper function for creating dummy ProteinSite objects

    :param protein: The protein instance
    :type protein: Protein
    :param site_json_dict: Dict of site description.
    :type site_json_dict: dict
    :return: The newly created protein site.
    :rtype: ProteinSite
    """
    if site_json_dict is None:
        site_json_dict = TestConfig.site_json
    protein_site = ProteinSite(protein=protein, site_description=site_json_dict)
    protein_site.save()
    return protein_site


def create_test_electrondensitymap():
    """Helper function for creating dummy ElectronDensityMap object

    :return: The newly created electron density map.
    :rtype: ElectronDensityMap
    """
    density_map = ElectronDensityMap()
    with TemporaryFile() as tmpfile:
        density_map.file.save('empty.ccp4', File(tmpfile))
        density_map.save()

    return density_map

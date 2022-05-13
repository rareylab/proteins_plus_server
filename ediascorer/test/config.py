"""Configuration for Unit Tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    protein = '4agm'
    protein_file = testdir / (protein + '.pdb')
    ligand_file = testdir / 'P86_A_400.sdf'
    ligand_file2 = testdir / 'P86_B_400.sdf'
    ligand_name3 = 'NXG_A_1294'
    ligand_file3 = testdir / 'NXG_A_1294.sdf'
    density_file = testdir / (protein + '.ccp4')
    atom_scores_file = testdir / 'edia_atom_scores.json'

"""Configuration for DoGSite tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    protein = '4agm'
    ligand = 'P86_A_400'
    chain_id = ''
    calc_subpockets = False
    ligand_bias = False
    protein_file = testdir / (protein + '.pdb')
    ligand_file = testdir / (ligand + '.sdf')

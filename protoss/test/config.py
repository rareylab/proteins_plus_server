"""Configuration for Unit Tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    protein = '4agm'
    protein_file = testdir / (protein + '.pdb')
    ligand_file = testdir / 'P86_A_400.sdf'

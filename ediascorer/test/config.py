"""Configuration for Unit Tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    protein = '4agm'
    protein_file = testdir / (protein + '.pdb')
    density_file = testdir / (protein + '.ccp4')
"""Configuration for Metalizer tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    protein = '4agm'
    protein_file = testdir / (protein + '.pdb')
    metalizer_result_file = testdir / 'metalizer_result.json'

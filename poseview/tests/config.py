"""Configuration for Poseview tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    protein = '4agn'
    protein_file = testdir / '4agn.pdb'
    ligand_file = testdir / 'NXG_A_1294.sdf'
    result_image = testdir / 'poseview.svg'

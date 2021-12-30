"""Configuration for Unit Tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    protein = '4agm'
    ligand = 'P86_A_400'
    ligand2 = 'P86_B_400'
    multi_ligands = 'multi_ligands'
    protein_file = testdir / (protein + '.pdb')
    ligand_file = testdir / (ligand + '.sdf')
    ligand2_file = testdir / (ligand + '.sdf')
    multi_ligands_file = testdir / (multi_ligands + '.sdf')

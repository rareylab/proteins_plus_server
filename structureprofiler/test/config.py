"""Configuration for Unit Tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    protein = '4agm'
    protein_file = testdir / (protein + '.pdb')
    density_file = testdir / (protein + '.ccp4')
    ligand_file = testdir / 'P86_A_400.sdf'

    protein_without_ligand = '2p58'
    protein_file_without_ligand = testdir / (protein_without_ligand + '.pdb')
    output_file = testdir / 'structureprofiler_output.json'

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
    density_file = testdir / (protein + '.ccp4')
    ligand_file = testdir / (ligand + '.sdf')
    ligand2_file = testdir / (ligand + '.sdf')
    multi_ligands_file = testdir / (multi_ligands + '.sdf')
    site_json = {'residue_ids': [
        {'name': 'LEU', 'position': '145', 'chain': 'A'},
        {'name': 'TRP', 'position': '146', 'chain': 'A'},
        {'name': 'VAL', 'position': '147', 'chain': 'A'},
        {'name': 'ASP', 'position': '148', 'chain': 'A'},
        {'name': 'SER', 'position': '149', 'chain': 'A'},
        {'name': 'THR', 'position': '150', 'chain': 'A'},
        {'name': 'PRO', 'position': '151', 'chain': 'A'},
        {'name': 'PRO', 'position': '152', 'chain': 'A'},
        {'name': 'THR', 'position': '155', 'chain': 'A'},
        {'name': 'CYS', 'position': '220', 'chain': 'A'},
        {'name': 'GLU', 'position': '221', 'chain': 'A'},
        {'name': 'PRO', 'position': '222', 'chain': 'A'},
        {'name': 'PRO', 'position': '223', 'chain': 'A'},
        {'name': 'SER', 'position': '227', 'chain': 'A'},
        {'name': 'ASP', 'position': '228', 'chain': 'A'},
        {'name': 'CYS', 'position': '229', 'chain': 'A'},
        {'name': 'THR', 'position': '230', 'chain': 'A'},
    ]}
    protein_1a3e = '1a3e'
    protein_file_1a3e = testdir / (protein_1a3e + '.pdb')
    edf_file_1a3e = testdir / '1a3e_residue_query.edf'
    af_protein = 'A0A024B5K5'
    af_protein_file = testdir / (af_protein + '.pdb.gz')

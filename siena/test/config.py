"""Configuration for Unit Tests"""
from pathlib import Path


class TestConfig:  # pylint: disable=too-few-public-methods
    """Constants for testing purposes"""
    testdir = Path('test_files/')
    siena_test_search_db = testdir / 'test_siena.db'
    siena_test_search_db_empty = testdir / 'test_siena_empty.db'
    protein_4agm = '4agm'
    ligand_4agm = 'P86_A_400'
    ligand2_4agm = 'P86_B_400'
    ligand_file_4agm = testdir / (ligand_4agm + '.sdf')
    ligand2_file_4agm = testdir / (ligand_4agm + '.sdf')
    protein_file_4agm = testdir / (protein_4agm + '.pdb')
    site_json_4agm = {'residue_ids': [
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
    site_json_not_existing_residue = {'residue_ids': [
        {'name': 'LEU', 'position': '1234567', 'chain': 'A'},
        {'name': 'TRP', 'position': '1234568', 'chain': 'A'},
        {'name': 'VAL', 'position': '1234569', 'chain': 'A'},
    ]}
    protein_1a3e = '1a3e'
    protein_file_1a3e = testdir / (protein_1a3e + '.pdb')
    edf_file_1a3e = testdir / '1a3e_residue_query.edf'

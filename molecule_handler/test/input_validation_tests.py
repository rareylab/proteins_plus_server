"""tests for input validators"""
from pathlib import Path
from django.core.files import File
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from proteins_plus.test.utils import PPlusTestCase
from .config import TestConfig
from .utils import create_test_protein, create_test_proteinsite, create_test_ligand
from ..input_validation import MoleculeInputValidator


class MoleculeInputValidatorTests(PPlusTestCase):
    """Molecular input validation tests"""

    def test_molecular_input_validation(self):
        """Test for validation of molecular input"""
        protein = create_test_protein()
        ligand = create_test_ligand(protein)
        with open(TestConfig.protein_file, 'r') as protein_file, \
                open(TestConfig.density_file, 'rb') as density_file, \
                open(TestConfig.ligand_file, 'r') as ligand_file:
            data = {'protein_id': protein.id,
                    'ligand_id': ligand.id,
                    'pdb_code': TestConfig.protein,
                    'uniprot_code': 'Q5VSL9',
                    'protein_file': protein_file,
                    'ligand_file': ligand_file,
                    'electron_density_map': File(density_file),
                    }
            validator = MoleculeInputValidator(data=data)
            self.assertTrue(validator.has_valid_protein_id())
            self.assertTrue(validator.has_valid_ligand_id())
            self.assertTrue(validator.has_valid_protein_file())
            self.assertTrue(validator.has_valid_ligand_file())
            self.assertTrue(validator.has_valid_electron_density_map())
            self.assertTrue(validator.has_valid_pdb_code())
            self.assertTrue(validator.has_valid_uniprot_code())

        self.assertRaises(NotFound,
                          MoleculeInputValidator(
                              data={'protein_id': 7358735897234}).has_valid_protein_id)
        self.assertRaises(NotFound,
                          MoleculeInputValidator(
                              data={'ligand_id': 7358735897234}).has_valid_ligand_id)
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'pdb_code': 'abcd'}).has_valid_pdb_code)
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'uniprot_code': 'abcd'}).has_valid_uniprot_code)
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_file': Path('no-valid-path')}).has_valid_protein_file)
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'ligand_file': Path('no-valid-path')}).has_valid_ligand_file)
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'electron_density_map': Path('no-valid-path.notanextension')}
                          ).has_valid_electron_density_map)

    def test_proteinsite_validation(self):
        """Test validation of protein site input"""

        # test retrieve protein site from DB with id
        protein = create_test_protein()
        site = create_test_proteinsite(protein)
        data = {'protein_site_id': site.id}
        validator = MoleculeInputValidator(data=data)
        self.assertTrue(validator.has_valid_protein_site_id())
        self.assertRaises(NotFound,
                          MoleculeInputValidator(
                              data={'protein_site_id': 7358735897234}).has_valid_protein_site_id)

        # test protein site from JSON input
        self.assertTrue(MoleculeInputValidator(
            data={'protein_site_json': TestConfig.site_json}).has_valid_protein_site_json())
        self.assertTrue(MoleculeInputValidator(
            data={'protein_site_json': {'residue_ids': [
                {'name': 'THR', 'position': '230A', 'chain': 'A'},
                {'name': 'THR', 'position': '-230', 'chain': 'A'},
                {'name': 'THR', 'position': '-231B', 'chain': 'A'},
            ]}}).has_valid_protein_site_json())
        self.assertFalse(
            MoleculeInputValidator(data={'nothing': '0'}).has_valid_protein_site_json())
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={
                                  'protein_site_json': {'nothing': 0}}).has_valid_protein_site_json)
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_site_json': {
                                  'residue_ids': 0}}).has_valid_protein_site_json)
        # duplicates
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_site_json': {'residue_ids': [
                                  {'name': 'THR', 'position': '230', 'chain': 'A'},
                                  {'name': 'THR', 'position': '230', 'chain': 'A'},
                              ]}}).has_valid_protein_site_json)
        # no name
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_site_json': {'residue_ids': [
                                  {'position': '230', 'chain': 'A'},
                              ]}}).has_valid_protein_site_json)
        # to long name
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_site_json': {'residue_ids': [
                                  {'name': 'THR4', 'position': '230', 'chain': 'A'},
                              ]}}).has_valid_protein_site_json)
        # no position
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_site_json': {'residue_ids': [
                                  {'name': 'THR', 'chain': 'A'},
                              ]}}).has_valid_protein_site_json)
        # invalid position
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_site_json': {'residue_ids': [
                                  {'name': 'THR', 'position': 'abc', 'chain': 'A'},
                              ]}}).has_valid_protein_site_json)
        # no chain
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_site_json': {'residue_ids': [
                                  {'name': 'THR', 'position': '1'},
                              ]}}).has_valid_protein_site_json)
        # too short chain
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_site_json': {'residue_ids': [
                                  {'name': 'THR', 'position': '1', 'chain': ''},
                              ]}}).has_valid_protein_site_json)
        # too long chain
        self.assertRaises(serializers.ValidationError,
                          MoleculeInputValidator(
                              data={'protein_site_json': {'residue_ids': [
                                  {'name': 'THR', 'position': '1', 'chain': 'ABC'},
                              ]}}).has_valid_protein_site_json)

"""Metalizer view tests"""
from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.test.utils import create_test_protein

from .config import TestConfig
from ..views import MetalizerView


class ViewTests(PPlusTestCase):
    """Metalizer view tests"""

    def test_protein_with_id(self):
        """Test metalizer with protein id"""
        input_protein = create_test_protein(TestConfig.protein)
        data = {
            'protein_id': input_protein.id,
            'residue_id': 1300,
            'chain_id': 'A',
            'name': 'ZN',
            'distance_threshold': 2.8
        }
        response = call_api(MetalizerView, 'post', data)
        self.assertEqual(response.status_code, 202)

    def test_protein_file(self):
        """Test metalizer with protein file"""
        with open(TestConfig.protein_file) as protein_file:
            data = {
                'protein_file': protein_file,
                'residue_id': 1300,
                'chain_id': 'A',
                'name': 'ZN',
                'distance_threshold': 2.8
            }
            response = call_api(MetalizerView, 'post', data)
        self.assertEqual(response.status_code, 202)

    def test_other_case(self):
        """Test metalizer with protein file"""
        with open(TestConfig.protein_file) as protein_file:
            data = {
                'protein_file': protein_file,
                'residue_id': 1300,
                'chain_id': 'B',
                'name': 'ZN',
                'distance_threshold': 3.0
            }
            response = call_api(MetalizerView, 'post', data)
        self.assertEqual(response.status_code, 202)

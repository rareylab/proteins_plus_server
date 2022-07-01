"""Metalizer view tests"""
from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.test.utils import create_test_protein

from ..views import MetalizerView, MetalizerJobViewSet, MetalizerInfoViewSet
from .config import TestConfig
from .utils import create_successful_metalizer_job


class ViewTests(PPlusTestCase):
    """Metalizer view tests"""

    def test_protein_with_id(self):
        """Test Metalizer with protein id"""
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
        """Test Metalizer with protein file"""
        with open(TestConfig.protein_file, encoding='utf8') as protein_file:
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
        """Test Metalizer with protein file"""
        with open(TestConfig.protein_file, encoding='utf8') as protein_file:
            data = {
                'protein_file': protein_file,
                'residue_id': 1300,
                'chain_id': 'B',
                'name': 'ZN',
                'distance_threshold': 3.0
            }
            response = call_api(MetalizerView, 'post', data)
        self.assertEqual(response.status_code, 202)

    def test_get_metalizer_job(self):
        """Test getting Metalizer results"""
        metalizer_job = create_successful_metalizer_job()
        response = call_api(
            MetalizerJobViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=metalizer_job.id
        )
        fields = [
            'input_protein',
            'residue_id',
            'chain_id',
            'name',
            'distance_threshold',
            'output_protein',
            'metalizer_info'
        ]
        for field in fields:
            self.assertIn(field, response.data)

        fields = ['id', 'info', 'parent_metalizer_job']
        response = call_api(
            MetalizerInfoViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=response.data['metalizer_info']
        )
        for field in fields:
            self.assertIn(field, response.data)

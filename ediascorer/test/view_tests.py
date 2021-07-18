"""tests for ediascorer views"""
from django.core.files import File

from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.test.utils import create_test_protein

from ..views import EdiascorerView
from .config import TestConfig

class ViewTests(PPlusTestCase):
    """Testcases for ediascorer views"""

    def test_post_protein_id_with_implicit_pdb_code(self):
        """Test ediascorer endpoint with protein id and implicit pdb code"""
        protein = create_test_protein()
        data = {'protein_id': protein.id}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_with_explicit_pdb_code(self):
        """Test ediascorer endpoint with protein id and explicit pdb code
          as query parameter"""
        protein = create_test_protein(pdb_code=None)
        data = {'pdb_code': TestConfig.protein, 'protein_id': protein.id}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_without_pdb_code(self):
        """Test ediascorer endpoint with protein id and without any pdb code"""
        protein = create_test_protein(pdb_code=None)
        data = {'protein_id': protein.id}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 400)

    def test_post_non_existing_protein_id(self):
        """Test ediascorer endpoint with non existing protein id"""
        data = {'protein_id': -1}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 404)

    def test_post_protein_id_with_density_file(self):
        """Test ediascorer endpoint with protein id, electron density file
            and without any pdb code"""
        protein = create_test_protein(pdb_code=None)
        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'electron_density_map': File(density_file),
                    'protein_id': protein.id}
            response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_with_wrong_pdb_code(self):
        """Test ediascorer endpoint with protein id and an invalid pdb code"""
        protein = create_test_protein(pdb_code=None)
        data = {'pdb_code': '1111', 'protein_id': protein.id}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

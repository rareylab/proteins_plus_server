"""tests for protoss views"""
from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.test.utils import create_test_protein
from ..views import ProtossView

class ViewTests(PPlusTestCase):
    """Testcases for protoss views"""
    def test_post_protein(self):
        """Test protoss view with existing protein id"""
        protein = create_test_protein()
        data = {'protein_id': protein.id}
        response = call_api(ProtossView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_non_existing_protein(self):
        """Test protoss view with non existing protein id"""
        data = {'protein_id': -1}
        response = call_api(ProtossView, 'post', data)

        self.assertEqual(response.status_code, 404)

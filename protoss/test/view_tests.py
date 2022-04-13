"""tests for protoss views"""
import uuid
from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.test.utils import create_test_protein
from .config import TestConfig
from ..views import ProtossView
from ..models import ProtossJob


class ViewTests(PPlusTestCase):
    """Testcases for protoss views"""

    def test_post_protein(self):
        """Test protoss view with existing protein id"""
        protein = create_test_protein()
        data = {'protein_id': protein.id}
        response = call_api(ProtossView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_file(self):
        """Test protoss view with a file upload"""
        with open(TestConfig.protein_file) as protein_file:
            data = {'protein_file': protein_file}
            response = call_api(ProtossView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_and_ligand_file(self):
        """Test protoss view with a protein and ligand file upload"""
        with open(TestConfig.protein_file) as protein_file:
            with open(TestConfig.ligand_file) as ligand_file:
                data = {'protein_file': protein_file, 'ligand_file': ligand_file}
                response = call_api(ProtossView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_non_existing_protein(self):
        """Test protoss view with non existing protein id"""
        data = {'protein_id': uuid.uuid4()}
        response = call_api(ProtossView, 'post', data)

        self.assertEqual(response.status_code, 404)

    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache via api"""
        protein1 = create_test_protein()
        job = ProtossJob(input_protein=protein1)
        job.set_hash_value()
        job.save()

        data = {'protein_id': protein1.id}
        response = call_api(ProtossView, 'post', data)

        self.assertTrue(response.data['retrieved_from_cache'])
        self.assertEqual(response.data['job_id'], str(job.id))

        protein2 = create_test_protein(empty=True)
        data = {'protein_id': protein2.id}
        response = call_api(ProtossView, 'post', data)

        self.assertFalse(response.data['retrieved_from_cache'])
        self.assertNotEqual(response.data['job_id'], str(job.id))

        data = {'protein_id': protein1.id,
                'use_cache': False}
        response = call_api(ProtossView, 'post', data)

        self.assertFalse(response.data['retrieved_from_cache'])
        self.assertNotEqual(response.data['job_id'], str(job.id))
        job2 = ProtossJob.objects.get(id=response.data['job_id'])
        self.assertIsNone(job2.hash_value)

"""tests for protoss database models"""
from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.test.utils import create_test_protein
from ..models import ProtossJob

class ModelTests(PPlusTestCase):
    """Testcases for protoss database models"""
    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache"""
        protein1 = create_test_protein()
        job = ProtossJob(input_protein=protein1)
        job.set_hash_value()
        job.save()

        protein2 = create_test_protein()
        job2 = ProtossJob(input_protein=protein2)
        cached_job = job2.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        protein3 = create_test_protein(pdb_code='1234')
        job3 = ProtossJob(input_protein=protein3)
        cached_job = job3.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

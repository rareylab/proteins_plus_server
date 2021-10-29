"""tests for ediascorer database models"""
from proteins_plus.test.utils import PPlusTestCase
from .utils import create_test_edia_job

class ModelTests(PPlusTestCase):
    """Testcases for ediascorer database models"""
    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache"""
        job = create_test_edia_job()
        job.set_hash_value()
        job.save()

        job2 = create_test_edia_job()
        cached_job = job2.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        job3 = create_test_edia_job(pdb_code='1234')
        cached_job = job3.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

"""tests for protoss database models"""
from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.models import Protein
from molecule_handler.test.utils import create_test_protein
from ..models import ProtossJob

from .utils import create_successful_protoss_job


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

    def test_job_delete_cascade(self):
        """Test cascading deletion behavior"""
        job = create_successful_protoss_job()
        input_protein = job.input_protein
        output_protein = job.output_protein
        job.delete()
        # deleting the job does not delete input or output
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Protein.objects.filter(id=output_protein.id).exists())

        job = create_successful_protoss_job()
        input_protein = job.input_protein
        output_protein = job.output_protein
        input_protein.delete()
        # deleting the input deletes the job but not the output
        self.assertFalse(ProtossJob.objects.filter(id=job.id).exists())
        self.assertTrue(Protein.objects.filter(id=output_protein.id).exists())

        job = create_successful_protoss_job()
        input_protein = job.input_protein
        output_protein = job.output_protein
        output_protein.delete()
        # deleting the output deletes the job but not the input
        self.assertFalse(ProtossJob.objects.filter(id=job.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())

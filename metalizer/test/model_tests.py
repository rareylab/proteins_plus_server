"""Metalizer model tests"""
from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.models import Protein

from ..models import MetalizerInfo, MetalizerJob
from .utils import create_test_metalizer_job, create_successful_metalizer_job


class ModelTests(PPlusTestCase):
    """Metalizer model tests"""

    def test_cache_behavior(self):
        """Test caching behavior of Metalizer jobs"""
        job = create_test_metalizer_job()
        job.set_hash_value()
        job.save()

        other_job = create_test_metalizer_job()
        cached_job = other_job.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        another_job = create_test_metalizer_job()
        another_job.distance_threshold = 3.0
        another_job.save()
        cached_job = another_job.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

    def test_job_delete_cascade(self):
        """Test cascading deletion behavior"""
        job = create_successful_metalizer_job()
        input_protein = job.input_protein
        output_protein = job.output_protein
        metalizer_info = job.metalizer_info
        job.delete()
        # deleting the job deletes the Metalizer info but not the protein
        self.assertFalse(MetalizerInfo.objects.filter(id=metalizer_info.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Protein.objects.filter(id=output_protein.id).exists())

        job = create_successful_metalizer_job()
        output_protein = job.output_protein
        input_protein = job.input_protein
        metalizer_info = job.metalizer_info
        metalizer_info.delete()
        # deleting the metalizer info deletes the job but not the protein
        self.assertFalse(MetalizerJob.objects.filter(id=job.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Protein.objects.filter(id=output_protein.id).exists())

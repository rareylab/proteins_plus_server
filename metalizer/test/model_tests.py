"""Metalizer model tests"""
from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.test.utils import create_test_protein

from .config import TestConfig
from ..models import MetalizerJob


class ModelTests(PPlusTestCase):
    """Metalizer model tests"""

    def test_cache_behavior(self):
        """Test caching behavior of Metalizer jobs"""
        input_protein = create_test_protein(TestConfig.protein)

        job = MetalizerJob(
            input_protein=input_protein,
            residue_id=1300,
            chain_id='A',
            name='ZN',
            distance_threshold=2.8
        )
        job.set_hash_value()
        job.save()

        other_job = MetalizerJob(
            input_protein=input_protein,
            residue_id=1300,
            chain_id='A',
            name='ZN',
            distance_threshold=2.8
        )
        cached_job = other_job.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        another_job = MetalizerJob(
            input_protein=input_protein,
            residue_id=1300,
            chain_id='A',
            name='ZN',
            distance_threshold=3.0  # changed distance threshold
        )
        cached_job = another_job.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

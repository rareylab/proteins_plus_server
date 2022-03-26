"""tests for molecule_handler database models"""
import os
from proteins_plus.test.utils import PPlusTestCase
from .config import TestConfig
from .utils import create_test_preprocesser_job
from ..tasks import preprocess_molecule_task
from ..models import PreprocessorJob

class ModelTests(PPlusTestCase):
    """Database model tests"""

    def test_ligand_images(self):
        """Test creation and deletion of ligand images"""
        job = create_test_preprocesser_job()

        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(pk=job.id)
        ligand = job.output_protein.ligand_set.first()
        image_path = ligand.image.path

        self.assertEqual(os.path.exists(image_path), True)
        ligand.delete()
        self.assertEqual(os.path.exists(image_path), False)

    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache"""
        job = create_test_preprocesser_job()
        job.set_hash_value()
        job.save()

        job2 = create_test_preprocesser_job()
        cached_job = job2.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        job3 = PreprocessorJob(pdb_code=TestConfig.protein)
        cached_job = job3.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

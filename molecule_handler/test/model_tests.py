"""tests for molecule_handler database models"""
import os
from proteins_plus.test.utils import PPlusTestCase

from ..tasks import preprocess_molecule_task
from ..models import PreprocessorJob, Protein, Ligand
from .config import TestConfig
from .utils import create_test_preprocesser_job, create_successful_preprocessor_job, \
    create_test_protein, create_test_ligand


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

    def test_job_delete_cascade(self):
        """Test cascading deletion behavior of the preprocessor job"""
        job = create_successful_preprocessor_job()
        protein = job.output_protein
        job.delete()
        # deleting the job does not delete the protein
        self.assertTrue(Protein.objects.filter(id=protein.id).exists())

        job = create_successful_preprocessor_job()
        protein = job.output_protein
        protein.delete()
        # deleting the protein deletes the job
        self.assertFalse(PreprocessorJob.objects.filter(id=job.id).exists())

    def test_ligand_delete_cascade(self):
        """Test cascading deletion behavior of the protein"""
        protein = create_test_protein()
        ligand = create_test_ligand(protein)
        ligand.delete()
        # deleting the ligand does not delete the protein
        self.assertTrue(Protein.objects.filter(id=protein.id))

        protein = create_test_protein()
        ligand = create_test_ligand(protein)
        protein.delete()
        # deleting the protein deletes the ligand
        self.assertFalse(Ligand.objects.filter(id=ligand.id))

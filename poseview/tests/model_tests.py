"""Tests for Poseview models"""
import os
from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.models import Protein, Ligand
from ..models import PoseviewJob
from .utils import create_poseview_job, create_successful_poseview_job


class ModelTests(PPlusTestCase):
    """Tests for Poseview models"""

    def test_poseview_images(self):
        """Test Poseview images are deleted"""
        job = create_successful_poseview_job()
        image_path = job.image.path
        self.assertTrue(os.path.exists(image_path))
        job.delete()
        self.assertFalse(os.path.exists(image_path))

    def test_caching(self):
        """Test Poseview job caching"""
        job = create_poseview_job()
        job.set_hash_value()
        job.save()

        job2 = create_poseview_job()
        cached_job = job2.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

    def test_cascading_delete(self):
        """Test cascading deletion behavior for the Poseview Job model"""
        job = create_successful_poseview_job()
        protein = job.input_protein
        ligand = job.input_ligand
        image_path = job.image.path
        job.delete()
        # deleting the job deletes the image but not the input
        self.assertTrue(Protein.objects.filter(id=protein.id).exists())
        self.assertTrue(Ligand.objects.filter(id=ligand.id).exists())
        self.assertFalse(os.path.exists(image_path))

        job = create_successful_poseview_job()
        protein = job.input_protein
        ligand = job.input_ligand
        image_path = job.image.path
        ligand.delete()
        # deleting the ligand deletes the image and job but not the protein
        self.assertTrue(Protein.objects.filter(id=protein.id).exists())
        self.assertFalse(PoseviewJob.objects.filter(id=job.id).exists())
        self.assertFalse(os.path.exists(image_path))

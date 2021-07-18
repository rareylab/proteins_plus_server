"""tests for molecule_handler database models"""
import os
from proteins_plus.test.utils import PPlusTestCase
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

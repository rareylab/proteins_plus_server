"""tests for protoss tasks"""
from proteins_plus.job_handler import Status
from proteins_plus.test.utils import PPlusTestCase

from molecule_handler.test.utils import create_test_protein, create_multiple_test_ligands

from ..tasks import protoss_protein_task
from ..models import ProtossJob

from .config import TestConfig

class TaskTests(PPlusTestCase):
    """Celery task tests"""
    def test_protoss_protein_without_ligands(self):
        """test of protoss workflow with protein"""
        input_protein = create_test_protein(TestConfig.protein+'_clean')

        job = ProtossJob(input_protein=input_protein)
        job.save()

        protoss_protein_task.run(job.id)
        job = ProtossJob.objects.get(pk=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)

    def test_protoss_protein_with_ligands(self):
        """test of protoss workflow with protein and multiple ligands"""
        input_protein = create_test_protein()
        create_multiple_test_ligands(input_protein)

        job = ProtossJob(input_protein=input_protein)
        job.save()

        protoss_protein_task.run(job.id)
        job = ProtossJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertEqual(job.output_protein.ligand_set.count(), 2)
        self.assertIsNotNone(job.output_protein.ligand_set.first().image)

    def test_protoss_non_existing_protein(self):
        """Test error behavior of protoss task"""
        input_protein = create_test_protein(TestConfig.protein+'_empty', empty=True)
        job = ProtossJob(input_protein=input_protein)
        job.save()

        with self.assertRaises(Exception):
            protoss_protein_task.run(job.id)

        job = ProtossJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.FAILURE)
        self.assertIsNotNone(job.error)
        self.assertEqual(job.error, "An error occurred during the execution of Protoss.")
        self.assertIsNotNone(job.error_detailed)
        self.assertTrue(job.error_detailed.startswith('Traceback'))
        self.assertIsNone(job.output_protein)

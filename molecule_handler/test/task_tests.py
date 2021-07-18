"""tests for molecule_handler tasks"""
import os
import subprocess

from django.conf import settings

from proteins_plus.job_handler import Status
from proteins_plus.test.utils import PPlusTestCase

from ..tasks import preprocess_molecule_task
from ..models import PreprocessorJob

from .config import TestConfig
from .utils import create_test_preprocesser_job

class TaskTests(PPlusTestCase):
    """Celery task tests"""
    def test_preprocessor_available(self):
        """Test the preprocessor binary exists at the correct location and is licensed"""
        path = settings.BINARIES['preprocessor']
        self.assertTrue(
            os.path.exists(path), f'Preprocessor binary does not exist at {path}')
        completed_process = subprocess.run(
            path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        # 64 == ArgumentError, which means the preprocessor is ready to accept arguments
        self.assertEqual(completed_process.returncode, 64,
                         'Preprocessor ran with unexpected error code. Is it licensed?')

    def test_preprocess_molecule(self):
        """Test the preprocessor correctly processes a protein file on it's own"""
        job = create_test_preprocesser_job(ligand_filepath=None)
        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertEqual(job.output_protein.ligand_set.count(), 2)

    def test_preprocess_molecule_with_ligand(self):
        """Test the preprocessor correctly processes a protein with an explicitly set ligand"""
        job = create_test_preprocesser_job()

        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)

        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertEqual(job.output_protein.ligand_set.count(), 1)

    def test_preprocess_molecule_with_multisdf(self):
        """Test preprocessing of molecule with a multi sdf ligand file"""
        job = create_test_preprocesser_job(ligand_filepath = TestConfig.multi_ligands_file)

        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)

        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertEqual(job.output_protein.ligand_set.count(), 2)

    def test_preprocess_molecule_error(self):
        """Test that the PreprocessorJob's status set to FAILURE if the file contains errors"""
        job = PreprocessorJob(
            protein_name='',
            pdb_code=None,
            protein_string='',
        )
        job.save()
        with self.assertRaises(Exception):
            preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)

        self.assertEqual(job.status, Status.FAILURE)
        self.assertIsNotNone(job.error)
        self.assertEqual(job.error, "An error occurred during the execution of Preprocessor.")
        self.assertIsNotNone(job.error_detailed)
        self.assertTrue(job.error_detailed.startswith('Traceback'))
        self.assertIsNone(job.output_protein)

    def test_preprocess_wrong_pdb_code(self):
        """Test the error behaviour if a non valid pdb code is provided"""
        job = PreprocessorJob(
            protein_name='',
            pdb_code='1111',
            protein_string=None,
        )
        job.save()

        with self.assertRaises(RuntimeError):
            preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)

        self.assertEqual(job.status, Status.FAILURE)
        self.assertIsNotNone(job.error)
        self.assertEqual(job.error, "An error occurred during the execution of Preprocessor.")
        self.assertIsNotNone(job.error_detailed)
        self.assertTrue(job.error_detailed.startswith('Traceback'))
        self.assertIsNone(job.output_protein)

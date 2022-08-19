"""tests for molecule_handler tasks"""
from pathlib import Path
from unittest.mock import patch

from django.test import override_settings

from proteins_plus.job_handler import Status
from proteins_plus.test.utils import PPlusTestCase, is_tool_available
from .external_tests import MockRequest
from ..external import PDBResource

from ..tasks import preprocess_molecule_task
from ..models import PreprocessorJob

from .config import TestConfig
from .utils import create_test_preprocessor_job


class TaskTests(PPlusTestCase):
    """Celery task tests"""

    def test_available(self):
        """Test if binary exists at the correct location and is licensed"""
        self.assertEqual(is_tool_available('preprocessor'), 64,
                         'Ran with unexpected error code. Is it licensed?')

    def test_preprocess_molecule(self):
        """Test the preprocessor correctly processes a protein file on its own"""
        job = create_test_preprocessor_job(ligand_filepath=None)
        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertEqual(job.output_protein.ligand_set.count(), 2)
        for ligand in job.output_protein.ligand_set.all():
            self.assertIsNotNone(ligand.image)

    def test_preprocess_molecule_pdb_code(self):
        """Test the preprocessor correctly processes a pdb_code on its own"""
        job = create_test_preprocessor_job(pdb_code=TestConfig.protein, ligand_filepath=None)
        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertEqual(job.output_protein.ligand_set.count(), 2)
        for ligand in job.output_protein.ligand_set.all():
            self.assertIsNotNone(ligand.image)

    def test_preprocess_molecule_with_ligand(self):
        """Test the preprocessor correctly processes a protein with an explicitly set ligand"""
        job = create_test_preprocessor_job()

        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)

        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertEqual(job.output_protein.ligand_set.count(), 1)

    def test_preprocess_molecule_pdb_code_with_ligand(self):
        """Test the preprocessor correctly processes a pdb_code with an explicitly set ligand"""
        job = create_test_preprocessor_job(pdb_code=TestConfig.protein,
                                           ligand_filepath=TestConfig.ligand_file)
        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)

        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertEqual(job.output_protein.ligand_set.count(), 1)

    def test_preprocess_molecule_with_multisdf(self):
        """Test preprocessing of molecule with a multi sdf ligand file"""
        job = create_test_preprocessor_job(ligand_filepath=TestConfig.multi_ligands_file)

        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)

        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertEqual(job.output_protein.ligand_set.count(), 2)

    def test_preprocess_molecule_error(self):
        """Test that the PreprocessorJob's status set to FAILURE if the file contains errors"""
        job = PreprocessorJob()
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

    @override_settings(LOCAL_PDB_MIRROR_DIR=Path('test_files'))
    def test_preprocess_wrong_pdb_code(self):
        """Test the error behaviour if a non valid pdb code is provided"""
        job = PreprocessorJob(pdb_code='1111')
        job.save()
        with self.assertRaises(RuntimeError), patch.object(PDBResource, '_external_request',
                                                           MockRequest.get_failed_mock_request):
            preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(id=job.id)

        self.assertEqual(job.status, Status.FAILURE)
        self.assertIsNotNone(job.error)
        self.assertEqual(job.error, "An error occurred during the execution of Preprocessor.")
        self.assertIsNotNone(job.error_detailed)
        self.assertTrue(job.error_detailed.startswith('Traceback'))
        self.assertIsNone(job.output_protein)

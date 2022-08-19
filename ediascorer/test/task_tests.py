"""tests for ediascorer tasks"""
from pathlib import Path
from django.test import override_settings

from proteins_plus.job_handler import Status
from proteins_plus.test.utils import PPlusTestCase, is_tool_available
from molecule_handler.test.utils import create_test_ligand
from ..tasks import ediascore_protein_task
from ..models import EdiaJob
from .config import TestConfig
from .utils import create_test_edia_job


class TaskTests(PPlusTestCase):
    """Celery task tests"""

    def test_available(self):
        """Test if binary exists at the correct location and is licensed"""
        self.assertEqual(is_tool_available('ediascorer'), 64,
                         'Ran with unexpected error code. Is it licensed?')

    def test_ediascore_protein_from_file(self):
        """Test ediascorer binary with uploading electron density file"""
        edia_job = create_test_edia_job()
        ediascore_protein_task.run(edia_job.id)
        edia_job = EdiaJob.objects.get(id=edia_job.id)
        self.assertIsNotNone(edia_job.electron_density_map.file)
        self.assertEqual(edia_job.status, Status.SUCCESS)
        atom_scores = edia_job.edia_scores.atom_scores
        self.assertIsNotNone(atom_scores)
        for (key, value) in atom_scores.items():
            self.assertIsInstance(key, str)
            _ = int(key)
            self.assertEqual(len(value.keys()), 11)
            break
        structure_scores = edia_job.edia_scores.structure_scores
        self.assertIsNotNone(structure_scores)
        self.assertEqual(len(structure_scores.keys()), 397)

    def test_ediascore_protein_with_ligand_from_file(self):
        """Test ediascorer binary with uploading electron density file"""
        edia_job = create_test_edia_job()
        ligand = create_test_ligand(
            edia_job.input_protein,
            ligand_name=TestConfig.ligand_name3,
            ligand_filepath=TestConfig.ligand_file3
        )
        edia_job.input_ligand = ligand
        edia_job.save()
        ediascore_protein_task.run(edia_job.id)
        edia_job = EdiaJob.objects.get(id=edia_job.id)
        self.assertIsNotNone(edia_job.electron_density_map.file)
        self.assertEqual(edia_job.status, Status.SUCCESS)
        atom_scores = edia_job.edia_scores.atom_scores
        self.assertIsNotNone(atom_scores)
        for (key, value) in atom_scores.items():
            self.assertIsInstance(key, str)
            _ = int(key)
            self.assertEqual(len(value.keys()), 11)
            break
        structure_scores = edia_job.edia_scores.structure_scores
        self.assertIsNotNone(structure_scores)
        self.assertEqual(len(structure_scores.keys()), 398)  # one more ligand

    @override_settings(LOCAL_DENSITY_MIRROR_DIR=Path('test_files'))
    def test_ediascore_protein_from_pdb(self):
        """Test ediascorer binary without uploading electron density file"""
        edia_job = create_test_edia_job(density_filepath=None)

        ediascore_protein_task.run(edia_job.id)
        edia_job = EdiaJob.objects.get(id=edia_job.id)
        self.assertIsNotNone(edia_job.electron_density_map.file)
        self.assertEqual(edia_job.status, Status.SUCCESS)
        scores = edia_job.edia_scores.atom_scores
        self.assertIsNotNone(scores)
        for (key, value) in scores.items():
            self.assertIsInstance(key, str)
            _ = int(key)
            self.assertEqual(len(value.keys()), 11)
            break

    def test_ediascore_protein_without_file_and_pdb_code(self):
        """Test error behaviour of ediascorer when neither density file
            nor pdb code is given"""
        edia_job = create_test_edia_job(pdb_code=None, density_filepath=None)

        with self.assertRaises(RuntimeError):
            ediascore_protein_task.run(edia_job.id)

        edia_job = EdiaJob.objects.get(id=edia_job.id)
        self.assertEqual(edia_job.status, Status.FAILURE)
        self.assertIsNotNone(edia_job.error)
        self.assertEqual(edia_job.error, "An error occurred during the execution of EDIAscorer.")
        self.assertIsNotNone(edia_job.error_detailed)
        self.assertTrue(edia_job.error_detailed.startswith('Traceback'))
        self.assertIsNone(edia_job.electron_density_map)

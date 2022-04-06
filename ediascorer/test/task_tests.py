"""tests for ediascorer tasks"""
from proteins_plus.job_handler import Status
from proteins_plus.test.utils import PPlusTestCase, is_tool_available
from ..tasks import ediascore_protein_task
from ..models import EdiaJob
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
        scores = edia_job.atom_scores.scores
        self.assertIsNotNone(scores)
        for (key, value) in scores.items():
            self.assertIsInstance(key, str)
            _ = int(key)
            self.assertEqual(len(value.keys()), 11)
            break

    def test_ediascore_protein_from_pdb(self):
        """Test ediascorer binary without uploading electron density file"""
        edia_job = create_test_edia_job(density_filepath=None)

        ediascore_protein_task.run(edia_job.id)
        edia_job = EdiaJob.objects.get(id=edia_job.id)
        self.assertIsNotNone(edia_job.electron_density_map.file)
        self.assertEqual(edia_job.status, Status.SUCCESS)
        scores = edia_job.atom_scores.scores
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

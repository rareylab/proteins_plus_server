"""tests for ediascorer database models"""
from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.models import Protein

from ..models import AtomScores, EdiaJob
from .utils import create_test_edia_job, create_successful_edia_job


class ModelTests(PPlusTestCase):
    """Testcases for ediascorer database models"""

    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache"""
        job = create_test_edia_job()
        job.set_hash_value()
        job.save()

        job2 = create_test_edia_job()
        cached_job = job2.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        job3 = create_test_edia_job(pdb_code='1234')
        cached_job = job3.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

    def test_job_delete_cascade(self):
        """Test cascading deletion behavior"""
        job = create_successful_edia_job()
        atom_scores = job.atom_scores
        input_protein = job.input_protein
        output_protein = job.output_protein
        job.delete()
        # deleting the job deletes the atom scores but not the proteins
        self.assertFalse(AtomScores.objects.filter(id=atom_scores.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Protein.objects.filter(id=output_protein.id).exists())

        job = create_successful_edia_job()
        atom_scores = job.atom_scores
        input_protein = job.input_protein
        output_protein = job.output_protein
        atom_scores.delete()
        # deleting the atom scores deletes the job but not the proteins
        self.assertFalse(EdiaJob.objects.filter(id=job.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Protein.objects.filter(id=output_protein.id).exists())

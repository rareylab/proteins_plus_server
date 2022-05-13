"""tests for ediascorer database models"""
from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.models import Protein
from molecule_handler.test.utils import create_test_ligand

from ..models import EdiaScores, EdiaJob
from .config import TestConfig
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

        job4 = create_test_edia_job()
        ligand = create_test_ligand(job4.input_protein, ligand_filepath=TestConfig.ligand_file)
        job4.input_ligand = ligand
        job4.save()
        job4.set_hash_value()
        job4.save()

        job5 = create_test_edia_job()
        ligand = create_test_ligand(job5.input_protein, ligand_filepath=TestConfig.ligand_file)
        job5.input_ligand = ligand
        job5.save()
        cached_ligand_job = job5.retrieve_job_from_cache()
        self.assertIsNotNone(cached_ligand_job)

    def test_different_ligand_caching(self):
        """Test caching behavior with different ligands"""
        job = create_test_edia_job()
        protein = job.input_protein
        ligand = create_test_ligand(protein, ligand_filepath=TestConfig.ligand_file)
        job.input_ligand = ligand
        job.save()
        job.set_hash_value()
        job.save()

        job2 = create_test_edia_job()
        other_protein = job2.input_protein
        other_ligand = create_test_ligand(other_protein, ligand_filepath=TestConfig.ligand_file2)
        job2.input_ligand = other_ligand
        job2.save()
        cached_job = job2.retrieve_job_from_cache()
        # different ligands should produce different jobs
        self.assertIsNone(cached_job)

    def test_job_delete_cascade(self):
        """Test cascading deletion behavior"""
        job = create_successful_edia_job()
        edia_scores = job.edia_scores
        input_protein = job.input_protein
        output_protein = job.output_protein
        job.delete()
        # deleting the job deletes the atom scores but not the proteins
        self.assertFalse(EdiaScores.objects.filter(id=edia_scores.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Protein.objects.filter(id=output_protein.id).exists())

        job = create_successful_edia_job()
        edia_scores = job.edia_scores
        input_protein = job.input_protein
        output_protein = job.output_protein
        edia_scores.delete()
        # deleting the atom scores deletes the job but not the proteins
        self.assertFalse(EdiaJob.objects.filter(id=job.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Protein.objects.filter(id=output_protein.id).exists())

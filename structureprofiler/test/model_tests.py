"""tests for StructureProfiler database models"""
from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.models import Protein, ElectronDensityMap
from molecule_handler.test.utils import create_test_ligand, create_test_protein, TestConfig

from ..models import StructureProfilerJob, StructureProfilerOutput
from .utils import create_test_structureprofiler_job, create_successful_structureprofiler_job


class ModelTests(PPlusTestCase):
    """Testcases for Structureprofiler database models"""

    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache"""
        job = create_test_structureprofiler_job()
        job.set_hash_value()
        job.save()

        job2 = create_test_structureprofiler_job()
        cached_job = job2.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        job3 = create_test_structureprofiler_job(pdb_code='1234')
        cached_job = job3.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

        job4 = create_test_structureprofiler_job()
        ligand = create_test_ligand(job4.input_protein, ligand_name=TestConfig.ligand,
                                    ligand_filepath=TestConfig.ligand_file)
        job4.input_ligand = ligand
        job4.save()
        job4.set_hash_value()
        job4.save()

        job5 = create_test_structureprofiler_job()
        ligand = create_test_ligand(job5.input_protein, ligand_name=TestConfig.ligand,
                                    ligand_filepath=TestConfig.ligand_file)
        job5.input_ligand = ligand
        job5.save()
        cached_ligand_job = job5.retrieve_job_from_cache()
        self.assertIsNotNone(cached_ligand_job)

    def test_different_ligand_caching(self):
        """Test caching behavior with different ligands"""

        protein = create_test_protein()
        ligand = create_test_ligand(protein, ligand_name=TestConfig.ligand,
                                    ligand_filepath=TestConfig.ligand_file)
        job = StructureProfilerJob(input_protein=protein, input_ligand=ligand)
        job.set_hash_value()
        job.save()

        protein.ligand_set.first().delete()
        ligand2 = create_test_ligand(protein, ligand_name=TestConfig.ligand2,
                                     ligand_filepath=TestConfig.ligand2_file)
        job2 = StructureProfilerJob(input_protein=protein, input_ligand=ligand2)
        cached_job = job2.retrieve_job_from_cache()
        # different ligands should produce different jobs
        self.assertIsNone(cached_job)

    def test_job_delete_cascade(self):
        """Test cascading deletion behavior"""
        job = create_successful_structureprofiler_job()
        output_data = job.output_data
        input_protein = job.input_protein
        electron_density = job.electron_density_map
        job.delete()

        # deleting the job deletes the output_data but not the protein and electron density map
        self.assertFalse(StructureProfilerOutput.objects.filter(id=output_data.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(ElectronDensityMap.objects.filter(id=electron_density.id).exists())

        job = create_successful_structureprofiler_job()

        output_data = job.output_data
        input_protein = job.input_protein
        electron_density = job.electron_density_map
        output_data.delete()

        # deleting the output_data deletes the job but not the proteins or electron density map
        self.assertFalse(StructureProfilerJob.objects.filter(id=job.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(ElectronDensityMap.objects.filter(id=electron_density.id).exists())

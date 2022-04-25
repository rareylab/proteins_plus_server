"""tests for structureprofiler_tasks"""
from proteins_plus.job_handler import Status
from proteins_plus.test.utils import PPlusTestCase, is_tool_available
from molecule_handler.test.utils import create_test_protein, create_multiple_test_ligands
from ..tasks import structureprofiler_protein_task
from ..models import StructureProfilerJob
from .config import TestConfig
from .utils import create_test_structureprofiler_job


class TaskTests(PPlusTestCase):
    """Celery task tests"""

    def test_available(self):
        """Test if binary exists at the correct location and is licensed"""
        self.assertEqual(is_tool_available('structureprofiler'), 65,
                         'Ran with unexpected error code. Is it licensed?')

    def test_structureprofiler_non_existing_protein(self):
        """Test error behavior of structureprofiler task"""
        # leads to following error:
        # .terminate called after throwing an instance of 'std::out_of_range'
        input_protein = create_test_protein(TestConfig.protein + '_empty', empty=True)
        job = StructureProfilerJob(
            input_protein=input_protein, density_file_pdb_code=TestConfig.protein
        )
        job.save()
        with self.assertRaises(Exception):
            structureprofiler_protein_task.run(job.id)
        job = StructureProfilerJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.FAILURE)
        self.assertIsNotNone(job.error)
        self.assertEqual(job.error, "An error occurred during the execution of StructureProfiler.")
        self.assertIsNotNone(job.error_detailed)
        self.assertTrue(job.error_detailed.startswith('Traceback'))
        self.assertIsNone(job.output_data)

    def test_structureprofiler_protein_from_file(self):
        """Test structureprofiler binary with uploading electron density file"""
        structureprofiler_job = create_test_structureprofiler_job(
            density_file_path=TestConfig.density_file
        )
        structureprofiler_protein_task.run(structureprofiler_job.id)
        structureprofiler_job = StructureProfilerJob.objects.get(id=structureprofiler_job.id)
        self.assertIsNotNone(structureprofiler_job.electron_density_map.file)
        self.assertEqual(structureprofiler_job.status, Status.SUCCESS)
        self.assertIsNone(structureprofiler_job.error)
        self.assertIsNotNone(structureprofiler_job.output_data)
        self.assertIsNotNone(structureprofiler_job.output_data.output_data)
        data = structureprofiler_job.output_data.output_data
        self.assertEqual(len(data), 3)
        self.assertIn('complex', data)
        self.assertIn('ligands', data)
        self.assertIn('active_sites', data)

        self.assertGreater(len(data['complex']), 0)
        self.assertGreater(len(data['ligands']['1']), 0)
        self.assertGreater(len(data['active_sites']['1']), 0)

    def test_structureprofiler_protein_from_pdb(self):
        """Test structureprofiler binary without uploading electron density file"""
        structureprofiler_job = create_test_structureprofiler_job(density_file_path=None)
        structureprofiler_protein_task(structureprofiler_job.id)
        structureprofiler_job = StructureProfilerJob.objects.get(id=structureprofiler_job.id)
        self.assertIsNotNone(structureprofiler_job.electron_density_map.file)
        self.assertEqual(structureprofiler_job.status, Status.SUCCESS)
        self.assertIsNone(structureprofiler_job.error)
        self.assertIsNotNone(structureprofiler_job.output_data)
        self.assertIsNotNone(structureprofiler_job.output_data.output_data)
        data = structureprofiler_job.output_data.output_data
        self.assertEqual(len(data), 3)
        self.assertIn('complex', data)
        self.assertIn('ligands', data)
        self.assertIn('active_sites', data)
        self.assertGreater(len(data['complex']), 0)
        self.assertGreater(len(data['ligands']['1']), 0)
        self.assertGreater(len(data['active_sites']['1']), 0)

    def test_structureprofiler_protein_without_file_and_pdb_code(self):
        """Test structureprofiler binary when neither density file
            nor pdb code is given"""
        structureprofiler_job = create_test_structureprofiler_job(
            pdb_code=None, density_file_path=None)
        structureprofiler_protein_task(structureprofiler_job.id)
        structureprofiler_job = StructureProfilerJob.objects.get(id=structureprofiler_job.id)
        self.assertEqual(structureprofiler_job.status, Status.SUCCESS)
        self.assertIsNone(structureprofiler_job.error)
        self.assertIsNone(structureprofiler_job.electron_density_map)
        self.assertIsNotNone(structureprofiler_job.output_data)
        self.assertIsNotNone(structureprofiler_job.output_data.output_data)
        data = structureprofiler_job.output_data.output_data
        self.assertEqual(len(data), 3)
        self.assertIn('complex', data)
        self.assertIn('ligands', data)
        self.assertIn('active_sites', data)
        self.assertGreater(len(data['complex']), 0)
        self.assertGreater(len(data['ligands']['1']), 0)
        self.assertGreater(len(data['active_sites']['1']), 0)

    def test_structureprofiler_protein_without_ligand(self):
        """ Test structureprofiler binary with protein without ligands"""
        input_protein = create_test_protein(
            protein_filepath=TestConfig.protein_file_without_ligand,
            pdb_code=None, protein_name=TestConfig.protein_without_ligand)
        structureprofiler_job = StructureProfilerJob(input_protein=input_protein)
        structureprofiler_job.save()
        structureprofiler_protein_task(structureprofiler_job.id)
        structureprofiler_job = StructureProfilerJob.objects.get(id=structureprofiler_job.id)
        self.assertEqual(structureprofiler_job.status, Status.SUCCESS)
        self.assertIsNone(structureprofiler_job.error)
        self.assertIsNone(structureprofiler_job.electron_density_map)
        self.assertIsNotNone(structureprofiler_job.output_data)
        self.assertIsNotNone(structureprofiler_job.output_data.output_data)
        data = structureprofiler_job.output_data.output_data
        self.assertEqual(len(data), 3)
        self.assertIn('complex', data)
        self.assertIn('ligands', data)
        self.assertIn('active_sites', data)
        self.assertGreater(len(data['complex']), 0)
        self.assertEqual(len(data['ligands']), 0)
        self.assertEqual(len(data['active_sites']), 0)

    def test_structureprofiler_protein_with_ligands(self):
        """test of structureprofiler workflow with protein and multiple ligands"""
        input_protein = create_test_protein()
        create_multiple_test_ligands(input_protein)
        structureprofiler_job = StructureProfilerJob(input_protein=input_protein)
        structureprofiler_job.save()
        structureprofiler_protein_task(structureprofiler_job.id)
        structureprofiler_job = StructureProfilerJob.objects.get(id=structureprofiler_job.id)

        self.assertEqual(structureprofiler_job.status, Status.SUCCESS)
        data = structureprofiler_job.output_data.output_data
        self.assertIsNotNone(data)
        #parsing specific ligands to structureprofiler leads to duplication of ligands in results
        self.assertGreater(len(data['ligands']), 0)
        self.assertGreater(len(data['complex']), 0)
        self.assertGreater(len(data['active_sites']), 0)

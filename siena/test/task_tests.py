"""tests for siena tasks"""
from molecule_handler.protein_site_handler import ProteinSiteHandler
from molecule_handler.test.utils import create_test_protein
from proteins_plus.job_handler import Status
from proteins_plus.test.utils import PPlusTestCase, is_tool_available
from .config import TestConfig
from .utils import create_test_siena_job, TmpSienaDB
from ..tasks import siena_protein_task
from ..models import SienaJob
from ..settings import SienaSettings


class TaskTests(PPlusTestCase):
    """Celery task tests"""

    def setUp(self):
        """Test set up"""
        self.original_siena_search_db = SienaSettings.SIENA_SEARCH_DB

    def tearDown(self):
        """Test tear down"""
        SienaSettings.SIENA_SEARCH_DB = self.original_siena_search_db

    def test_available(self):
        """Test if binary exists at the correct location and is licensed"""
        self.assertEqual(is_tool_available('siena'), 64,
                         'Ran with unexpected error code. Is it licensed?')

    def test_siena_protein_ligand_input(self):
        """test of siena workflow with protein and ligand input"""

        # global overwrite of siena-app-settings
        SienaSettings.SIENA_SEARCH_DB = TestConfig.siena_test_search_db

        job = create_test_siena_job(pdb_code=TestConfig.protein_4agm,
                                    protein_filepath=TestConfig.protein_file_4agm,
                                    ligand=TestConfig.ligand_4agm)
        job.save()

        siena_protein_task.run(job.id)
        job = SienaJob.objects.get(pk=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_info)
        self.assertIsNotNone(job.output_info.alignment)
        self.assertIsNotNone(job.output_info.statistic)
        self.assertIsNotNone(job.output_proteins)

        self.assertEqual(job.output_proteins.count(), 2)

        count_ligands = len(list(job.get_ensemble_ligands()))
        self.assertEqual(count_ligands, 2)

    def test_siena_protein_site_input(self):
        """test of siena workflow with protein and protein site input"""

        # global overwrite of siena-app-settings
        SienaSettings.SIENA_SEARCH_DB = TestConfig.siena_test_search_db

        inputs = [(TestConfig.protein_4agm, TestConfig.protein_file_4agm,
                   TestConfig.site_json_4agm),
                  (TestConfig.protein_1a3e, TestConfig.protein_file_1a3e,
                   ProteinSiteHandler.edf_to_json(TestConfig.edf_file_1a3e)
                   )]
        expected_outputs = [(2, 2), (1, 0)]
        assert len(inputs) == len(expected_outputs)

        for i, input_elem in enumerate(inputs):
            protein_name, protein_file, site_json = input_elem
            exp_nof_proteins, exp_nof_ligands = expected_outputs[i]

            job = create_test_siena_job(pdb_code=protein_name,
                                        protein_filepath=protein_file,
                                        site=site_json)
            job.save()

            siena_protein_task.run(job.id)
            job = SienaJob.objects.get(pk=job.id)
            self.assertEqual(job.status, Status.SUCCESS)
            self.assertIsNotNone(job.output_info)
            self.assertIsNotNone(job.output_info)
            self.assertIsNotNone(job.output_info.alignment)
            self.assertIsNotNone(job.output_info.statistic)
            self.assertIsNotNone(job.output_proteins)

            self.assertEqual(job.output_proteins.count(), exp_nof_proteins)

            count_ligands = len(list(job.get_ensemble_ligands()))
            self.assertEqual(count_ligands, exp_nof_ligands)

            stats_dict = job.output_info.statistic
            self.assertIsNotNone(stats_dict)
            self.assertEqual(len(stats_dict), exp_nof_proteins)

    def test_no_ligand_nor_site(self):
        """Test invalid input without ligand or site"""

        # global overwrite of siena-app-settings
        SienaSettings.SIENA_SEARCH_DB = TestConfig.siena_test_search_db

        job = SienaJob(
            input_protein=create_test_protein(pdb_code=TestConfig.protein_4agm,
                                              protein_filepath=TestConfig.protein_file_4agm),
            input_site=None,
            input_ligand=None
        )
        job.save()

        with self.assertRaises(ValueError):
            siena_protein_task.run(job.id)

        siena_job = SienaJob.objects.get(id=job.id)
        self.assertEqual(siena_job.status, Status.FAILURE)
        self.assertIsNotNone(siena_job.error)
        self.assertEqual(siena_job.error,
                         "An error occurred during the execution of Siena.")
        self.assertIsNotNone(siena_job.error_detailed)
        self.assertTrue(siena_job.error_detailed.startswith('Traceback'))

    def test_no_search_results(self):
        """Test no results from SIENA search"""

        # global overwrite of siena-app-settings
        SienaSettings.SIENA_SEARCH_DB = TestConfig.siena_test_search_db_empty

        job = create_test_siena_job(pdb_code=TestConfig.protein_4agm,
                                    protein_filepath=TestConfig.protein_file_4agm,
                                    ligand=TestConfig.ligand_4agm)
        job.save()

        siena_protein_task.run(job.id)
        job = SienaJob.objects.get(pk=job.id)

        self.assertEqual(job.output_proteins.count(), 0)
        self.assertIsNone(job.output_info)

        siena_job = SienaJob.objects.get(id=job.id)
        self.assertEqual(siena_job.status, Status.SUCCESS)
        self.assertIsNone(siena_job.error)

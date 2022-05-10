"""DoGSite task tests"""
from proteins_plus.test.utils import PPlusTestCase, is_tool_available
from proteins_plus.models import Status

from ..models import DoGSiteJob
from ..tasks import dogsite_task
from .utils import create_test_dogsite_job


class TaskTests(PPlusTestCase):
    """DoGSite task tests"""

    def test_available(self):
        """Test if binary exists at the correct location and is licensed"""
        self.assertEqual(is_tool_available('dogsite'), 64,
                         'Ran with unexpected error code. Is it licensed?')

    def test_dogsite(self):
        """Test DoGSite execution produces expected results"""
        job = create_test_dogsite_job()
        dogsite_task.run(job.id)
        job = DoGSiteJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_pockets)
        self.assertIsNotNone(job.output_densities)
        self.assertIsNotNone(job.dogsite_info)

        self.assertEqual(job.output_pockets.count(), 7)
        self.assertEqual(job.output_densities.count(), 7)

    def test_dogsite_without_ligand(self):
        """Test DoGSite execution without ligand producing expected results"""
        job = create_test_dogsite_job(ligand_name=None)
        dogsite_task.run(job.id)
        job = DoGSiteJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_pockets)
        self.assertIsNotNone(job.output_densities)
        self.assertIsNotNone(job.dogsite_info)

        self.assertEqual(job.output_pockets.count(), 7)
        self.assertEqual(job.output_densities.count(), 7)

    def test_dogsite_with_ligand_bias_and_ligandfile(self):
        """Test DoGSite execution with ligand bias and ligand file producing expected results"""
        job = create_test_dogsite_job(ligand_bias=True)
        dogsite_task.run(job.id)
        job = DoGSiteJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_pockets)
        self.assertIsNotNone(job.output_densities)
        self.assertIsNotNone(job.dogsite_info)

        self.assertEqual(job.output_pockets.count(), 7)
        self.assertEqual(job.output_densities.count(), 7)

    def test_dogsite_with_ligand_bias_and_without_ligandfile(self):
        """Test DoGSite execution with ligand bias and without ligand file producing expected
         results"""
        job = create_test_dogsite_job(ligand_name=None, ligand_bias=True)
        dogsite_task.run(job.id)
        job = DoGSiteJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_pockets)
        self.assertIsNotNone(job.output_densities)
        self.assertIsNotNone(job.dogsite_info)

        self.assertEqual(job.output_pockets.count(), 7)
        self.assertEqual(job.output_densities.count(), 7)

    def test_dogsite_with_subpockets(self):
        """Test DoGSite execution with subpockets producing expected results"""
        job = create_test_dogsite_job(calc_subpockets=True)
        dogsite_task.run(job.id)
        job = DoGSiteJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_pockets)
        self.assertIsNotNone(job.output_densities)
        self.assertIsNotNone(job.dogsite_info)

        self.assertEqual(job.output_pockets.count(), 9)
        self.assertEqual(job.output_densities.count(), 9)

    def test_dogsite_with_chainid(self):
        """Test DoGSite execution with chainid producing expected results"""
        job = create_test_dogsite_job(chain_id='B')
        dogsite_task.run(job.id)
        job = DoGSiteJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_pockets)
        self.assertIsNotNone(job.output_densities)
        self.assertIsNotNone(job.dogsite_info)

        self.assertEqual(job.output_pockets.count(), 3)
        self.assertEqual(job.output_densities.count(), 3)

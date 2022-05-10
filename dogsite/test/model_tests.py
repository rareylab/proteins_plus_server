"""DoGSite model tests"""
from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.models import ElectronDensityMap, Ligand, Protein, ProteinSite

from ..models import DoGSiteInfo, DoGSiteJob
from .utils import create_test_dogsite_job, create_successful_dogsite_job


class ModelTests(PPlusTestCase):
    """DoGSite model tests"""

    def test_cache_behavior(self):
        """Test caching behavior of DoGSite jobs"""
        job = create_test_dogsite_job()
        job.set_hash_value()
        job.save()

        other_job = create_test_dogsite_job()
        cached_job = other_job.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        another_job = create_test_dogsite_job()
        another_job.calc_subpockets = True
        another_job.save()
        cached_job = another_job.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

    def test_job_delete_cascade(self):
        """Test cascading deletion behavior"""
        job = create_successful_dogsite_job()
        input_protein = job.input_protein
        input_ligand = job.input_ligand
        dogsite_info = job.dogsite_info
        output_pockets_ids = [p.id for p in job.output_pockets.all()]
        output_densities_ids = [p.id for p in job.output_densities.all()]
        job.delete()
        # deleting the job deletes the DoGSite info but not the input and output proteins
        self.assertFalse(DoGSiteJob.objects.filter(id=job.id).exists())
        self.assertFalse(DoGSiteInfo.objects.filter(id=dogsite_info.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Ligand.objects.filter(id=input_ligand.id).exists())
        self.assertGreater(len(output_pockets_ids), 0)
        for out_pocket_id in output_pockets_ids:
            self.assertTrue(ProteinSite.objects.filter(id=out_pocket_id).exists())
        self.assertGreater(len(output_densities_ids), 0)
        for out_density_id in output_densities_ids:
            self.assertTrue(ElectronDensityMap.objects.filter(id=out_density_id).exists())

        # test delete DoGSiteInfo
        job = create_successful_dogsite_job()
        input_protein = job.input_protein
        input_ligand = job.input_ligand
        dogsite_info = job.dogsite_info
        output_pockets_ids = [p.id for p in job.output_pockets.all()]
        output_densities_ids = [p.id for p in job.output_densities.all()]
        dogsite_info.delete()
        # deleting the output info deletes the job but not the proteins and ligands
        self.assertFalse(DoGSiteJob.objects.filter(id=job.id).exists())
        self.assertFalse(DoGSiteInfo.objects.filter(id=dogsite_info.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Ligand.objects.filter(id=input_ligand.id).exists())
        self.assertGreater(len(output_pockets_ids), 0)
        for out_pocket_id in output_pockets_ids:
            self.assertTrue(ProteinSite.objects.filter(id=out_pocket_id).exists())
        for out_density_id in output_densities_ids:
            self.assertTrue(ElectronDensityMap.objects.filter(id=out_density_id).exists())

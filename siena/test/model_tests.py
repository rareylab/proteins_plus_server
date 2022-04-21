"""tests for SIENA database models"""
import copy

from molecule_handler.models import Protein, Ligand, ProteinSite
from molecule_handler.test.utils import create_test_protein, create_test_ligand, \
    create_test_proteinsite
from proteins_plus.test.utils import PPlusTestCase

from .config import TestConfig
from .utils import create_successful_siena_job
from ..models import SienaJob, SienaInfo


class ModelTests(PPlusTestCase):
    """Testcases for siena database models"""

    def test_cache_behaviour_ligand_input(self):
        """Test storing and retrieving objects from cache using ligand input"""

        # test with ligand
        protein1 = create_test_protein(pdb_code=TestConfig.protein_4agm,
                                       protein_filepath=TestConfig.protein_file_4agm,
                                       protein_name=TestConfig.protein_4agm)
        ligand1 = create_test_ligand(protein1,
                                     ligand_name=TestConfig.ligand_4agm,
                                     ligand_filepath=TestConfig.ligand_file_4agm)
        job = SienaJob(input_protein=protein1, input_ligand=ligand1)
        job.set_hash_value()
        job.save()

        protein2 = create_test_protein(pdb_code=TestConfig.protein_4agm,
                                       protein_filepath=TestConfig.protein_file_4agm,
                                       protein_name=TestConfig.protein_4agm)
        ligand2 = create_test_ligand(protein2,
                                     ligand_name=TestConfig.ligand_4agm,
                                     ligand_filepath=TestConfig.ligand_file_4agm)
        job2 = SienaJob(input_protein=protein2, input_ligand=ligand2)
        cached_job = job2.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        protein3 = create_test_protein(pdb_code='1234')
        ligand3 = create_test_ligand(protein3,
                                     ligand_name=TestConfig.ligand_4agm,
                                     ligand_filepath=TestConfig.ligand_file_4agm)
        job3 = SienaJob(input_protein=protein3, input_ligand=ligand3)
        cached_job = job3.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

    def test_cache_behaviour_site_input(self):
        """Test storing and retrieving objects from cache using protein sites input"""

        protein1 = create_test_protein(pdb_code=TestConfig.protein_4agm,
                                       protein_filepath=TestConfig.protein_file_4agm,
                                       protein_name=TestConfig.protein_4agm)
        site1 = create_test_proteinsite(protein1, TestConfig.site_json_4agm)
        job = SienaJob(input_protein=protein1, input_site=site1)
        job.set_hash_value()
        job.save()

        # is same as protein1 + site1. Should be cached.
        protein2 = create_test_protein(pdb_code=TestConfig.protein_4agm,
                                       protein_filepath=TestConfig.protein_file_4agm,
                                       protein_name=TestConfig.protein_4agm)
        site2 = create_test_proteinsite(protein1, TestConfig.site_json_4agm)
        job2 = SienaJob(input_protein=protein2, input_site=site2)
        cached_job = job2.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        # has different ordering in site residue list. But is same as protein1. Should be cached.
        protein3 = create_test_protein(pdb_code=TestConfig.protein_4agm,
                                       protein_filepath=TestConfig.protein_file_4agm,
                                       protein_name=TestConfig.protein_4agm)
        different_order_json = copy.deepcopy(TestConfig.site_json_4agm)
        different_order_json['residue_ids'][0], different_order_json['residue_ids'][1] = \
            different_order_json['residue_ids'][1], different_order_json['residue_ids'][0]
        site3 = create_test_proteinsite(protein3, different_order_json)
        job3 = SienaJob(input_protein=protein3, input_site=site3)
        cached_job = job3.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        # nonsense protein. Should not be cached
        protein4 = create_test_protein(pdb_code='4242')
        site4 = create_test_proteinsite(protein4, {'residue_ids': [{'42': 42}]})
        job4 = SienaJob(input_protein=protein4, input_site=site4)
        cached_job = job4.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

    def test_job_delete_cascade(self):
        """Test cascading deletion behaviour"""

        # test delete job with ligand input
        job = create_successful_siena_job(use_site=False)
        input_protein = job.input_protein
        input_ligand = job.input_ligand
        output_info = job.output_info
        output_proteins_ids = [p.id for p in job.output_proteins.all()]
        job.delete()
        # deleting the job deletes the output_info but not the input and output_proteins
        self.assertFalse(SienaJob.objects.filter(id=job.id).exists())
        self.assertFalse(SienaInfo.objects.filter(id=output_info.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Ligand.objects.filter(id=input_ligand.id).exists())
        self.assertGreater(len(output_proteins_ids), 0)
        for out_protein_id in output_proteins_ids:
            self.assertTrue(Protein.objects.filter(id=out_protein_id).exists())

        # test delete SienaInfo/output_info with ligand input
        job = create_successful_siena_job(use_site=False)
        input_protein = job.input_protein
        input_ligand = job.input_ligand
        output_info = job.output_info
        output_proteins_ids = [p.id for p in job.output_proteins.all()]
        output_info.delete()
        # deleting the output info deletes the job but not the proteins and ligands
        self.assertFalse(SienaJob.objects.filter(id=job.id).exists())
        self.assertFalse(SienaInfo.objects.filter(id=output_info.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(Ligand.objects.filter(id=input_ligand.id).exists())
        self.assertGreater(len(output_proteins_ids), 0)
        for out_protein_id in output_proteins_ids:
            self.assertTrue(Protein.objects.filter(id=out_protein_id).exists())

        # test delete job with protein site input
        job = create_successful_siena_job(use_site=True)
        input_protein = job.input_protein
        input_site = job.input_site
        output_info = job.output_info
        output_proteins_ids = [p.id for p in job.output_proteins.all()]
        job.delete()
        # deleting the job deletes the output_info but not the input and output_proteins
        self.assertFalse(SienaJob.objects.filter(id=job.id).exists())
        self.assertFalse(SienaInfo.objects.filter(id=output_info.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(ProteinSite.objects.filter(id=input_site.id).exists())
        self.assertGreater(len(output_proteins_ids), 0)
        for out_protein_id in output_proteins_ids:
            self.assertTrue(Protein.objects.filter(id=out_protein_id).exists())

        # test delete SienaInfo/output_info with protein site input
        job = create_successful_siena_job(use_site=True)
        input_protein = job.input_protein
        input_site = job.input_site
        output_info = job.output_info
        output_proteins_ids = [p.id for p in job.output_proteins.all()]
        output_info.delete()
        # deleting the output info deletes the job but not the proteins, site
        self.assertFalse(SienaJob.objects.filter(id=job.id).exists())
        self.assertFalse(SienaInfo.objects.filter(id=output_info.id).exists())
        self.assertTrue(Protein.objects.filter(id=input_protein.id).exists())
        self.assertTrue(ProteinSite.objects.filter(id=input_site.id).exists())
        self.assertGreater(len(output_proteins_ids), 0)
        for out_protein_id in output_proteins_ids:
            self.assertTrue(Protein.objects.filter(id=out_protein_id).exists())

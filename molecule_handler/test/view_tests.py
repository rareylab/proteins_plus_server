"""tests for molecule_handler views"""
from django.core.files import File

from proteins_plus.test.utils import PPlusTestCase, call_api

from ..views import ProteinUploadView, ProteinViewSet, LigandViewSet, PreprocessorJobViewSet
from ..models import PreprocessorJob

from .config import TestConfig
from .utils import create_test_protein, create_multiple_test_ligands, create_test_preprocesser_job


class ViewTests(PPlusTestCase):
    """Testcases for the molecule_handler views"""

    def test_molecule_upload_protein(self):
        """Test upload of Protein"""
        with open(TestConfig.protein_file, 'rb') as protein_file:
            data = {'protein_file': File(protein_file)}
            response = call_api(ProteinUploadView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_molecule_upload_protein_by_pdb_code(self):
        """Test upload of Protein by pdb code"""
        data = {'pdb_code': TestConfig.protein}
        response = call_api(ProteinUploadView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_molecule_upload_protein_and_ligand(self):
        """Test upload of Protein and Ligand"""
        with open(TestConfig.protein_file, 'rb') as protein_file, \
                open(TestConfig.ligand_file, 'rb') as ligand_file:
            data = {'protein_file': File(protein_file),
                    'ligand_file': File(ligand_file)}
            response = call_api(ProteinUploadView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_molecule_upload_protein_wrong_filetype(self):
        """Test Protein upload with wrong filetype"""
        with open(TestConfig.testdir / (TestConfig.protein + '.txt'), 'rb') as protein_file:
            data = {'protein_file': File(protein_file)}
            response = call_api(ProteinUploadView, 'post', data)

        self.assertEqual(response.status_code, 400)

    def test_molecule_upload_ligand_wrong_filetype(self):
        """Test Ligand upload with wrong filetype"""
        with open(TestConfig.protein_file, 'rb') as protein_file, \
                open(TestConfig.testdir / (TestConfig.ligand + '.txt'), 'rb') as ligand_file:
            data = {'protein_file': File(protein_file),
                    'ligand_file': File(ligand_file)}
            response = call_api(ProteinUploadView, 'post', data)

        self.assertEqual(response.status_code, 400)

    def test_molecule_upload_empty(self):
        """Test upload with empty data"""
        response = call_api(ProteinUploadView, 'post')

        self.assertEqual(response.status_code, 400)

    def test_protein_upload_with_wrong_pdb_code(self):
        """Test upload with an invalid pdb code"""
        data = {'pdb_code': 'i111'}
        response = call_api(ProteinUploadView, 'post', data)

        self.assertEqual(response.status_code, 400)

    def test_protein_upload_with_wrong_uniprot_code(self):
        """Test upload with an invalid pdb code"""
        data = {'uniprot_code': '1112'}
        response = call_api(ProteinUploadView, 'post', data)

        self.assertEqual(response.status_code, 400)

    def test_retrieve_protein(self):
        """Test retrieve and list Protein behavior"""
        protein = create_test_protein()
        create_test_protein()

        response = call_api(ProteinViewSet, 'get',
                            viewset_actions={'get': 'retrieve'},
                            pk=protein.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(protein.id))

        response = call_api(ProteinViewSet, 'get',
                            viewset_actions={'get': 'list'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_ligand(self):
        """Test retrieve and list Ligand behavior"""
        protein = create_test_protein()
        ligand, _ = create_multiple_test_ligands(protein)

        response = call_api(LigandViewSet, 'get',
                            viewset_actions={'get': 'retrieve'},
                            pk=ligand.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(ligand.id))

        response = call_api(LigandViewSet, 'get',
                            viewset_actions={'get': 'list'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_preprocessor_job(self):
        """Test retrieve and list PreprocessorJob behavior"""
        job = create_test_preprocesser_job()
        create_test_preprocesser_job()

        response = call_api(PreprocessorJobViewSet, 'get',
                            viewset_actions={'get': 'retrieve'},
                            pk=job.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(job.id))

        response = call_api(PreprocessorJobViewSet, 'get',
                            viewset_actions={'get': 'list'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache via api"""
        job = create_test_preprocesser_job()
        job.set_hash_value()
        job.save()

        with open(TestConfig.protein_file, 'rb') as protein_file, \
                open(TestConfig.ligand_file, 'rb') as ligand_file:
            data = {'protein_file': File(protein_file),
                    'pdb_code': TestConfig.protein,
                    'ligand_file': File(ligand_file)}
            response = call_api(ProteinUploadView, 'post', data)

        self.assertTrue(response.data['retrieved_from_cache'])
        self.assertEqual(response.data['job_id'], str(job.id))

        data = {'pdb_code': TestConfig.protein}
        response = call_api(ProteinUploadView, 'post', data)

        self.assertFalse(response.data['retrieved_from_cache'])
        self.assertNotEqual(response.data['job_id'], str(job.id))

        with open(TestConfig.protein_file, 'rb') as protein_file, \
                open(TestConfig.ligand_file, 'rb') as ligand_file:
            data = {'protein_file': File(protein_file),
                    'pdb_code': TestConfig.protein,
                    'ligand_file': File(ligand_file),
                    'use_cache': False}
            response = call_api(ProteinUploadView, 'post', data)

        self.assertFalse(response.data['retrieved_from_cache'])
        self.assertNotEqual(response.data['job_id'], str(job.id))
        job2 = PreprocessorJob.objects.get(id=response.data['job_id'])
        self.assertIsNone(job2.hash_value)
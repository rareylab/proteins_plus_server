"""tests for molecule_handler views"""
import tempfile

from django.core.files import File

from proteins_plus.test.utils import PPlusTestCase, call_api

from ..views import ProteinUploadView, ProteinViewSet, LigandViewSet, PreprocessorJobViewSet, \
    ProteinSiteViewSet, ElectronDensityMapViewSet, PreprocessorJobDataViewSet
from ..models import PreprocessorJob

from .config import TestConfig
from .utils import create_test_protein, create_multiple_test_ligands, \
    create_test_preprocessor_job, create_test_proteinsite, create_test_electrondensitymap


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

    def test_molecule_upload_protein_by_pdb_code_and_ligand(self):
        """Test upload of Protein by pdb code"""
        with open(TestConfig.ligand_file, 'rb') as ligand_file:
            data = {'pdb_code':  TestConfig.protein,
                    'ligand_file': File(ligand_file)}
            response = call_api(ProteinUploadView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_molecule_upload_protein_wrong_filetype(self):
        """Test Protein upload with wrong filetype"""
        wrong_filetype_path = TestConfig.testdir / (TestConfig.protein + '.txt')
        with open(wrong_filetype_path, 'rb') as protein_file:
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

    def test_molecule_upload_bad_ligand(self):
        """Test upload with empty data"""

        with open(TestConfig.protein_file, 'rb') as protein_file, \
                tempfile.NamedTemporaryFile() as ligand_file:

            # empty ligand file with valid protein file
            data = {'protein_file': File(protein_file),
                    'ligand_file': File(ligand_file)}
            response = call_api(ProteinUploadView, 'post', data)
            self.assertEqual(response.status_code, 400)

            # empty ligand file with valid PDB code
            data = {'pdb_code': TestConfig.protein,
                    'ligand_file': File(ligand_file)}
            response = call_api(ProteinUploadView, 'post', data)
            self.assertEqual(response.status_code, 400)

            # write some content in the empty ligand file
            ligand_file.write(b'Definitely not a valid molecule file')

            # nonsense ligand file with valid protein file
            data = {'protein_file': File(protein_file),
                    'ligand_file': File(ligand_file)}
            response = call_api(ProteinUploadView, 'post', data)
            self.assertEqual(response.status_code, 400)

            # nonsense ligand file with valid PDB code
            ligand_file.write(b'Definitely not a valid molecule file')
            data = {'pdb_code': TestConfig.protein,
                    'ligand_file': File(ligand_file)}
            response = call_api(ProteinUploadView, 'post', data)
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

        fields = [
            'id',
            'name',
            'pdb_code',
            'file_type',
            'ligand_set',
            'file_string',
            'date_created',
            'date_last_accessed'
        ]
        for field in fields:
            self.assertIn(field, response.data)

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
        fields = ['id', 'name', 'protein', 'file_type', 'file_string', 'image']
        for field in fields:
            self.assertIn(field, response.data)

        response = call_api(LigandViewSet, 'get',
                            viewset_actions={'get': 'list'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_protein_site(self):
        """Test retrieve and list ProteinSite behavior"""
        protein = create_test_protein()
        site = create_test_proteinsite(protein)
        protein2 = create_test_protein()
        create_test_proteinsite(protein2)

        response = call_api(ProteinSiteViewSet, 'get',
                            viewset_actions={'get': 'retrieve'},
                            pk=site.id)
        self.assertEqual(response.status_code, 200)
        fields = ['id', 'protein', 'site_description']
        for field in fields:
            self.assertIn(field, response.data)

        response = call_api(ProteinSiteViewSet, 'get',
                            viewset_actions={'get': 'list'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_electron_density_map(self):
        """Test retrieve and list ElectronDensityMap behavior"""
        density = create_test_electrondensitymap()
        create_test_electrondensitymap()

        response = call_api(ElectronDensityMapViewSet, 'get',
                            viewset_actions={'get': 'retrieve'},
                            pk=density.id)
        self.assertEqual(response.status_code, 200)
        fields = ['id', 'file', 'date_created', 'date_last_accessed']
        for field in fields:
            self.assertIn(field, response.data)

        response = call_api(ElectronDensityMapViewSet, 'get',
                            viewset_actions={'get': 'list'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_preprocessor_job(self):
        """Test retrieve and list PreprocessorJob behavior"""
        job = create_test_preprocessor_job()
        create_test_preprocessor_job()

        response = call_api(PreprocessorJobViewSet, 'get',
                            viewset_actions={'get': 'retrieve'},
                            pk=job.id)
        self.assertEqual(response.status_code, 200)
        fields = ['pdb_code', 'uniprot_code', 'input_data', 'output_protein']
        for field in fields:
            self.assertIn(field, response.data)

        response = call_api(PreprocessorJobViewSet, 'get',
                            viewset_actions={'get': 'list'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_preprocessor_job_data(self):
        """Test retrieve and list PreprocessorJobData behavior"""

        job = create_test_preprocessor_job()
        create_test_preprocessor_job()

        response = call_api(PreprocessorJobDataViewSet, 'get',
                            viewset_actions={'get': 'retrieve'},
                            pk=job.input_data.id)
        self.assertEqual(response.status_code, 200)
        fields = ['parent_preprocessor_job', 'input_protein_string', 'input_protein_file_type',
                  'input_ligand_string', 'input_ligand_file_type']

        for field in fields:
            self.assertIn(field, response.data)

        response = call_api(PreprocessorJobDataViewSet, 'get',
                            viewset_actions={'get': 'list'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache via api"""
        job = create_test_preprocessor_job()
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

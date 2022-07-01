"""tests for ediascorer views"""
import uuid
from django.core.files import File

from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.test.utils import create_test_protein

from ..views import EdiascorerView, EdiaJobViewSet, EdiaScoresViewSet
from ..models import EdiaJob
from .config import TestConfig
from .utils import create_successful_edia_job


class ViewTests(PPlusTestCase):
    """Testcases for ediascorer views"""

    def test_post_protein_id_with_implicit_pdb_code(self):
        """Test ediascorer endpoint with protein id and implicit pdb code"""
        protein = create_test_protein()
        data = {'protein_id': protein.id}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_file_with_explicit_pdb_code(self):
        """Test ediascorer endpoint with protein file and explicit pdb code"""
        with open(TestConfig.protein_file, encoding='utf8') as protein_file:
            data = {'pdb_code': TestConfig.protein, 'protein_file': protein_file}
            response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_and_ligand_file(self):
        """Test ediascorer endpoint with protein and ligand file"""
        with open(TestConfig.protein_file, encoding='utf8') as protein_file:
            with open(TestConfig.ligand_file, encoding='utf8') as ligand_file:
                data = {'protein_file': protein_file, 'ligand_file': ligand_file}
                response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_and_ligand_file(self):
        """Test ediascorer endpoint with protein id and ligand file"""
        protein = create_test_protein()
        with open(TestConfig.ligand_file, encoding='utf8') as ligand_file:
            data = {'protein_id': protein.id, 'ligand_file': ligand_file}
            response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

        # uploading the ligand file does not change the original protein
        self.assertFalse(protein.ligand_set.exists())
        job = EdiaJob.objects.get(id=response.data['job_id'])
        # the ligand from the file was associated with a copy of the protein
        self.assertTrue(job.input_protein.ligand_set.exists())

    def test_post_protein_id_with_explicit_pdb_code(self):
        """Test ediascorer endpoint with protein id and explicit pdb code
          as query parameter"""
        protein = create_test_protein(pdb_code=None)
        data = {'pdb_code': TestConfig.protein, 'protein_id': protein.id}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_without_pdb_code(self):
        """Test ediascorer endpoint with protein id and without any pdb code"""
        protein = create_test_protein(pdb_code=None)
        data = {'protein_id': protein.id}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 400)

    def test_post_non_existing_protein_id(self):
        """Test ediascorer endpoint with non existing protein id"""
        data = {'protein_id': uuid.uuid4()}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 404)

    def test_post_protein_id_with_density_file(self):
        """Test ediascorer endpoint with protein id, electron density file
            and without any pdb code"""
        protein = create_test_protein(pdb_code=None)
        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'electron_density_map': File(density_file),
                    'protein_id': protein.id}
            response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_with_wrong_pdb_code(self):
        """Test ediascorer endpoint with protein id and an invalid pdb code"""
        protein = create_test_protein(pdb_code=None)
        data = {'pdb_code': '1111', 'protein_id': protein.id}
        response = call_api(EdiascorerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache via api"""
        protein = create_test_protein()
        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'electron_density_map': File(density_file),
                    'pdb_code': TestConfig.protein,
                    'protein_id': protein.id}
            response1 = call_api(EdiascorerView, 'post', data)

        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'electron_density_map': File(density_file),
                    'protein_id': protein.id}
            response2 = call_api(EdiascorerView, 'post', data)

        self.assertTrue(response2.data['retrieved_from_cache'])
        self.assertEqual(response1.data['job_id'], response2.data['job_id'])

        data = {'pdb_code': TestConfig.protein,
                'protein_id': protein.id}
        response3 = call_api(EdiascorerView, 'post', data)

        self.assertFalse(response3.data['retrieved_from_cache'])
        self.assertNotEqual(response3.data['job_id'], response1.data['job_id'])

        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'electron_density_map': File(density_file),
                    'pdb_code': TestConfig.protein,
                    'protein_id': protein.id,
                    'use_cache': False}
            response4 = call_api(EdiascorerView, 'post', data)

        self.assertFalse(response4.data['retrieved_from_cache'])
        self.assertNotEqual(response4.data['job_id'], response1.data['job_id'])
        job = EdiaJob.objects.get(id=response4.data['job_id'])
        self.assertIsNone(job.hash_value)

    def test_get_edia_job_view(self):
        """Test getting EDIA results"""
        edia_job = create_successful_edia_job()
        response = call_api(
            EdiaJobViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=edia_job.id
        )
        fields = [
            'input_protein',
            'density_file_pdb_code',
            'electron_density_map',
            'edia_scores',
            'output_protein'
        ]
        for field in fields:
            self.assertIn(field, response.data)

        response = call_api(
            EdiaScoresViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=response.data['edia_scores']
        )
        fields = ['id', 'atom_scores', 'structure_scores', 'parent_edia_job']
        for field in fields:
            self.assertIn(field, response.data)

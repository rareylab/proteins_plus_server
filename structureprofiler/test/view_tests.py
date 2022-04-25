"""tests for structureprofiler views"""
import uuid
from django.core.files import File

from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.test.utils import create_test_protein

from ..views import StructureProfilerView, StructureProfilerJobViewSet, \
    StructureProfilerOutputViewSet
from ..models import StructureProfilerJob
from .config import TestConfig
from .utils import create_successful_structureprofiler_job


class ViewTests(PPlusTestCase):
    """Testcases for structureprofiler views"""

    def test_post_protein_id_with_implicit_pdb_code(self):
        """Test structureprofiler endpoint with protein id and implicit pdb code"""
        protein = create_test_protein()
        data = {'protein_id': protein.id}
        response = call_api(StructureProfilerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_file_with_explicit_pdb_code(self):
        """Test structureprofiler endpoint with protein file and explicit pdb code"""
        with open(TestConfig.protein_file) as protein_file:
            data = {'pdb_code': TestConfig.protein, 'protein_file': protein_file}
            response = call_api(StructureProfilerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_with_explicit_pdb_code(self):
        """Test structureprofiler endpoint with protein id and explicit pdb code
          as query parameter"""
        protein = create_test_protein(pdb_code=None)
        data = {'pdb_code': TestConfig.protein, 'protein_id': protein.id}
        response = call_api(StructureProfilerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_without_pdb_code(self):
        """Test structureprofiler endpoint with protein id and without any pdb code"""
        protein = create_test_protein(pdb_code=None)
        data = {'protein_id': protein.id}
        response = call_api(StructureProfilerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_with_density_file(self):
        """Test structureprofiler endpoint with protein id, electron density file
            and without any pdb code"""
        protein = create_test_protein(pdb_code=None)
        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'electron_density_map': File(density_file),
                    'protein_id': protein.id}
            response = call_api(StructureProfilerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_with_wrong_pdb_code(self):
        """Test structureprofiler endpoint with protein id and an invalid pdb code"""
        protein = create_test_protein(pdb_code=None)
        data = {'pdb_code': '1111', 'protein_id': protein.id}
        response = call_api(StructureProfilerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_post_protein_id_and_ligand_file(self):
        """Test structureprofilers endpoint with protein id and ligand file"""
        protein = create_test_protein()
        with open(TestConfig.ligand_file) as ligand_file:
            data = {'protein_id': protein.id, 'ligand_file': ligand_file}
            response = call_api(StructureProfilerView, 'post', data)

        self.assertEqual(response.status_code, 202)

        # uploading the ligand file does not change the original protein
        self.assertFalse(protein.ligand_set.exists())
        job = StructureProfilerJob.objects.get(id=response.data['job_id'])
        # the ligand from the file was associated with a copy of the protein
        self.assertTrue(job.input_protein.ligand_set.exists())

    def test_post_protein_and_ligand_file(self):
        """Test structureprofiler view with a protein and ligand file upload """
        with open(TestConfig.protein_file) as protein_file:
            with open(TestConfig.ligand_file) as ligand_file:
                data = {'protein_file': protein_file, 'ligand_file': ligand_file}
                response = call_api(StructureProfilerView, 'post', data)

        self.assertEqual(response.status_code, 202)

    def test_protein_density_map_and_ligand_file(self):
        """Test structureprofiler view with a protein,
         electron density map and ligand file upload
         """
        with open(TestConfig.protein_file) as protein_file:
            with open(TestConfig.ligand_file) as ligand_file:
                with open(TestConfig.density_file, 'rb') as density_file:
                    data = {'protein_file': protein_file, 'ligand_file': ligand_file,
                            'electron_density_map': density_file}
                    response = call_api(StructureProfilerView, 'post', data)
        self.assertEqual(response.status_code, 202)

    def test_post_non_existing_protein(self):
        """Test structureprofiler view with non existing protein id"""
        data = {'protein_id': uuid.uuid4()}
        response = call_api(StructureProfilerView, 'post', data)

        self.assertEqual(response.status_code, 404)

    def test_cache_behaviour(self):
        """Test storing and retrieving objects from cache via api"""
        protein = create_test_protein()
        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'electron_density_map': File(density_file),
                    'pdb_code': TestConfig.protein,
                    'protein_id': protein.id}
            response1 = call_api(StructureProfilerView, 'post', data)

        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'electron_density_map': File(density_file),
                    'protein_id': protein.id}
            response2 = call_api(StructureProfilerView, 'post', data)

        self.assertTrue(response2.data['retrieved_from_cache'])
        self.assertEqual(response1.data['job_id'], response2.data['job_id'])

        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'pdb_code': TestConfig.protein,
                    'protein_id': protein.id}
            response3 = call_api(StructureProfilerView, 'post', data)

        self.assertFalse(response3.data['retrieved_from_cache'])
        self.assertNotEqual(response3.data['job_id'], response1.data['job_id'])

        with open(TestConfig.density_file, 'rb') as density_file:
            data = {'electron_density_map': File(density_file),
                    'pdb_code': TestConfig.protein,
                    'protein_id': protein.id,
                    'use_cache': False}
            response4 = call_api(StructureProfilerView, 'post', data)

        self.assertFalse(response4.data['retrieved_from_cache'])
        self.assertNotEqual(response4.data['job_id'], response1.data['job_id'])
        job = StructureProfilerJob.objects.get(id=response4.data['job_id'])
        self.assertIsNone(job.hash_value)

    def test_get_structureprofilerjob_view(self):
        """Test getting Strutureprofiler results"""
        structureprofiler_job = create_successful_structureprofiler_job()
        response = call_api(
            StructureProfilerJobViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=structureprofiler_job.id
        )
        fields = [
            'input_protein',
            'density_file_pdb_code',
            'electron_density_map',
            'output_data'
        ]
        for field in fields:
            self.assertIn(field, response.data)

        response = call_api(
            StructureProfilerOutputViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=response.data['output_data']
        )
        fields = ['id', 'output_data', 'parent_structureprofiler_job']
        for field in fields:
            self.assertIn(field, response.data)

"""Poseview view tests"""
from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.models import Protein, Ligand

from ..views import PoseviewView, PoseviewJobViewSet
from .config import TestConfig
from .utils import create_successful_poseview_job


class ViewTests(PPlusTestCase):
    """Poseview view tests"""

    def test_query_with_ids(self):
        """Test Poseview with protein and ligand id"""
        with open(TestConfig.protein_file) as protein_file:
            input_protein = Protein.from_file(protein_file)
        input_protein.save()
        with open(TestConfig.ligand_file) as ligand_file:
            input_ligand = Ligand.from_file(ligand_file, input_protein)
        input_ligand.save()

        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
        }
        response = call_api(PoseviewView, 'post', data)
        self.assertEqual(response.status_code, 202)

    def test_query_with_files(self):
        """Test Poseview with protein and ligand files"""
        with open(TestConfig.protein_file) as protein_file:
            with open(TestConfig.ligand_file) as ligand_file:
                data = {
                    'protein_file': protein_file,
                    'ligand_file': ligand_file
                }
                response = call_api(PoseviewView, 'post', data)
        self.assertEqual(response.status_code, 202)

    def test_get_poseview_job(self):
        """Test getting Poseview results"""
        job = create_successful_poseview_job()
        response = call_api(
            PoseviewJobViewSet, 'get', viewset_actions={'get': 'retrieve'}, pk=job.id)
        fields = [
            'input_protein',
            'input_ligand',
            'image'
        ]
        for field in fields:
            self.assertIn(field, response.data)

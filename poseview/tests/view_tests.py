"""Poseview view tests"""
from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.models import Protein, Ligand

from ..models import PoseviewJob
from ..views import PoseviewView, PoseviewJobViewSet
from .config import TestConfig
from .utils import create_successful_poseview_job


class ViewTests(PPlusTestCase):
    """Poseview view tests"""

    def test_query_with_ids(self):
        """Test Poseview with protein and ligand id"""
        with open(TestConfig.protein_file, encoding='utf8') as protein_file:
            input_protein = Protein.from_file(protein_file)
        input_protein.save()
        with open(TestConfig.ligand_file, encoding='utf8') as ligand_file:
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
        with open(TestConfig.protein_file, encoding='utf8') as protein_file:
            with open(TestConfig.ligand_file, encoding='utf8') as ligand_file:
                data = {
                    'protein_file': protein_file,
                    'ligand_file': ligand_file
                }
                response = call_api(PoseviewView, 'post', data)
        self.assertEqual(response.status_code, 202)

    def test_query_with_protein_id_and_ligand_file(self):
        """Test poseview endpoint with protein id and ligand file"""
        with open(TestConfig.protein_file, encoding='utf8') as protein_file:
            input_protein = Protein.from_file(protein_file)
        input_protein.save()
        with open(TestConfig.ligand_file, encoding='utf8') as ligand_file:
            data = {
                'protein_id': input_protein.id,
                'ligand_file': ligand_file
            }
            response = call_api(PoseviewView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # uploading the ligand file does not change the original protein
        self.assertFalse(input_protein.ligand_set.exists())
        job = PoseviewJob.objects.get(id=response.data['job_id'])
        # the ligand from the file was associated with a copy of the protein
        self.assertTrue(job.input_protein.ligand_set.exists())

    def test_query_with_protein_id_and_ligand_from_other_protein(self):
        """Test poseview endpoint with protein id and ligand id from another protein"""
        with open(TestConfig.protein_file, encoding='utf8') as protein_file:
            input_protein = Protein.from_file(protein_file)
        input_protein.save()
        with open(TestConfig.protein_file, encoding='utf8') as protein_file:
            other_protein = Protein.from_file(protein_file)
        other_protein.save()
        with open(TestConfig.ligand_file, encoding='utf8') as ligand_file:
            input_ligand = Ligand.from_file(ligand_file, other_protein)
        input_ligand.save()

        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
        }
        response = call_api(PoseviewView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # uploading the ligand file does not change the original protein
        self.assertFalse(input_protein.ligand_set.exists())
        job = PoseviewJob.objects.get(id=response.data['job_id'])
        # the job ligand was associated with a copy of the protein
        self.assertTrue(job.input_protein.ligand_set.exists())
        self.assertEqual(job.input_protein.ligand_set.first().id, job.input_ligand.id)
        # the job ligand is also a copy to ensure protein and ligand have the same lifecycle
        self.assertNotEqual(job.input_ligand.id, input_ligand.id)

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

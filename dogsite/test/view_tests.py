"""DoGSite view tests"""
from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.test.utils import create_test_ligand, create_test_protein

from .config import TestConfig
from .utils import create_successful_dogsite_job
from ..views import DoGSiteView, DoGSiteJobViewSet, DoGSiteInfoViewSet


class ViewTests(PPlusTestCase):
    """DoGSite view tests"""

    def test_post_valid_queries(self):
        """Test DoGSite with valid input"""
        input_protein = create_test_protein(TestConfig.protein)
        input_ligand = create_test_ligand(input_protein)

        # protein id and ligand id
        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
            'chain_id': 'A',
            'calc_subpockets': False,
            'ligand_bias': False
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # protein file and ligand id
        with open(TestConfig.protein_file) as protein_file:
            data = {
                'protein_file': protein_file,
                'ligand_id': input_ligand.id,
                'chain_id': 'A',
                'calc_subpockets': False,
                'ligand_bias': False
            }
            response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # protein file and ligand file
        with open(TestConfig.protein_file) as protein_file:
            with open(TestConfig.ligand_file) as ligand_file:
                data = {
                    'protein_file': protein_file,
                    'ligand_file': ligand_file,
                    'chain_id': 'A',
                    'calc_subpockets': False,
                    'ligand_bias': False
                }
                response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # protein id and ligand file
        with open(TestConfig.ligand_file) as ligand_file:
            data = {
                'protein_id': input_protein.id,
                'ligand_file': ligand_file,
                'chain_id': 'A',
                'calc_subpockets': False,
                'ligand_bias': False
            }
            response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # without ligand id or file
        data = {
            'protein_id': input_protein.id,
            'chain_id': 'A',
            'calc_subpockets': False,
            'ligand_bias': False
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # analysis detail true or subpocket calculation
        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
            'chain_id': 'A',
            'calc_subpockets': True,
            'ligand_bias': False
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # ligand bias set to true
        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
            'chain_id': 'A',
            'calc_subpockets': False,
            'ligand_bias': True
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # analysis detail and ligand bias true
        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
            'chain_id': 'A',
            'calc_subpockets': True,
            'ligand_bias': True
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # without chain id
        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
            'calc_subpockets': False,
            'ligand_bias': False
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # blank chain id
        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
            'chain_id': '',
            'calc_subpockets': False,
            'ligand_bias': False
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # without analysis detail (fallback to default)
        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
            'ligand_bias': False
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # without ligand bias (fallback to default)
        data = {
            'protein_id': input_protein.id,
            'ligand_id': input_ligand.id,
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 202)

    def test_post_invalid_queries(self):
        """Test DoGSite with invalid input"""
        input_protein = create_test_protein(TestConfig.protein)
        input_ligand = create_test_ligand(input_protein)

        # no protein is not allowed
        data = {
            'ligand_id': input_ligand.id,
            'chain_id': 'A',
            'calc_subpockets': False,
            'ligand_bias': False
        }
        response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # protein id and protein file at the same time is not allowed
        with open(TestConfig.protein_file) as protein_file:
            data = {
                'protein_id': input_protein.id,
                'protein_file': protein_file,
                'ligand_id': input_ligand.id,
                'chain_id': 'A',
                'calc_subpockets': False,
                'ligand_bias': False
            }
            response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # ligand id and ligand file at the same time is not allowed
        with open(TestConfig.ligand_file) as ligand_file:
            data = {
                'protein_id': input_protein.id,
                'ligand_id': input_ligand.id,
                'ligand_file': ligand_file,
                'chain_id': 'A',
                'calc_subpockets': False,
                'ligand_bias': False
            }
            response = call_api(DoGSiteView, 'post', data)
        self.assertEqual(response.status_code, 400)

    def test_get_dogsite_job(self):
        """Test getting DoGSite results"""
        job = create_successful_dogsite_job()
        response = call_api(
            DoGSiteJobViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=job.id
        )
        fields = [
            'input_protein',
            'input_ligand',
            'chain_id',
            'calc_subpockets',
            'ligand_bias',
            'output_pockets',
            'output_densities',
            'dogsite_info',
        ]
        for field in fields:
            self.assertIn(field, response.data)

        fields = ['id', 'info', 'parent_dogsite_job']
        response = call_api(
            DoGSiteInfoViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=response.data['dogsite_info']
        )
        for field in fields:
            self.assertIn(field, response.data)

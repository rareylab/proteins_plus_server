"""tests for siena views"""
import json

from proteins_plus.test.utils import PPlusTestCase, call_api
from molecule_handler.test.utils import create_test_protein, create_test_ligand, \
    create_test_proteinsite

from .config import TestConfig
from .utils import create_successful_siena_job
from ..views import SienaView, SienaJobViewSet, SienaInfoViewSet


class ViewTests(PPlusTestCase):
    """Testcases for siena views"""

    def test_post_valid_queries(self):
        """Test siena endpoint with valid input"""
        protein = create_test_protein()
        ligand = create_test_ligand(protein)
        site = create_test_proteinsite(protein)
        site_json = json.dumps(TestConfig.site_json_4agm)

        # protein id and ligand id is allowed
        data = {'protein_id': protein.id, 'ligand_id': ligand.id}
        response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # protein file with ligand id is allowed
        with open(TestConfig.protein_file_4agm) as protein_file:
            data = {'protein_file': protein_file, 'ligand_id': ligand.id}
            response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # protein file with ligand file is allowed
        with open(TestConfig.protein_file_4agm) as protein_file:
            with open(TestConfig.ligand_file_4agm) as ligand_file:
                data = {'protein_file': protein_file, 'ligand_file': ligand_file}
                response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # protein id and site id is allowed
        data = {'protein_id': protein.id, 'protein_site_id': site.id}
        response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # protein id and site json is allowed
        data = {'protein_id': protein.id,
                'protein_site_json': site_json}
        response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # protein file and site id is allowed
        with open(TestConfig.protein_file_4agm) as protein_file:
            data = {'protein_file': protein_file, 'protein_site_id': site.id}
            response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 202)

        # protein file and site json is allowed
        with open(TestConfig.protein_file_4agm) as protein_file:
            data = {'protein_file': protein_file,
                    'protein_site_json': site_json}
            response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 202)

    def test_post_invalid_queries(self):
        """Test siena endpoint with invalid input"""
        protein = create_test_protein()
        ligand = create_test_ligand(protein)
        site = create_test_proteinsite(protein)
        site_json = json.dumps(TestConfig.site_json_4agm)

        # protein id with ligand file is not allowed
        with open(TestConfig.ligand_file_4agm) as ligand_file:
            data = {'protein_id': protein.id, 'ligand_file': ligand_file}
            response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # site id and site json is not allowed
        data = {'protein_id': protein.id, 'protein_site_id': site.id,
                'protein_site_json': site_json}
        response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # no protein not allowed
        data = {'ligand_id': ligand.id}
        response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # protein id with protein file is not allowed
        with open(TestConfig.protein_file_4agm) as protein_file:
            data = {'protein_id': protein.id, 'protein_file': protein_file, 'ligand_id': ligand.id}
            response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # no ligand and not site is not allowed
        data = {'protein_id': protein.id}
        response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # ligand id with ligand file is not allowed
        with open(TestConfig.ligand_file_4agm) as ligand_file:
            data = {'protein_id': protein.id, 'ligand_id': ligand.id, 'ligand_file': ligand_file}
            response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # site id with ligand file is not allowed
        with open(TestConfig.ligand_file_4agm) as ligand_file:
            data = {'protein_id': protein.id, 'protein_site_id': site.id,
                    'ligand_file': ligand_file}
            response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # site id with ligand id is not allowed
        data = {'protein_id': protein.id, 'protein_site_id': site.id, 'ligand_id': ligand.id}
        response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 400)

        # site id and site json is not allowed
        data = {'protein_id': protein.id, 'protein_site_id': site.id,
                'protein_site_json': TestConfig.site_json_4agm}
        response = call_api(SienaView, 'post', data)
        self.assertEqual(response.status_code, 400)

    def test_get_siena_job(self):
        """Test getting Siena results"""
        job = create_successful_siena_job()
        response = call_api(
            SienaJobViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=job.id
        )
        fields = [
            'input_protein',
            'input_ligand',
            'input_site',
            'output_info',
            'output_proteins'
        ]
        for field in fields:
            self.assertIn(field, response.data)

        fields = ['id', 'statistic', 'alignment', 'parent_siena_job']
        response = call_api(
            SienaInfoViewSet,
            'get',
            viewset_actions={'get': 'retrieve'},
            pk=response.data['output_info']
        )
        for field in fields:
            self.assertIn(field, response.data)

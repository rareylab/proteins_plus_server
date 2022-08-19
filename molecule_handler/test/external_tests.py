"""tests for external resources"""
from pathlib import Path

from django.test import override_settings
from unittest.mock import patch

from molecule_handler.external import PDBResource, DensityResource
from molecule_handler.test.config import TestConfig
from proteins_plus.test.utils import PPlusTestCase


class MockRequest:
    """Simple object to mock an external request"""

    def __init__(self, status_code,  text='', content=b''):
        """Construct a new object

        :param status_code: The http code.
        :type status_code: int
        :param text: text content of the mock request.
        :type text: str.
        :param content: byte content of the mock request.
        :type content: bytes
        """
        self.status_code = status_code
        self.text = text
        self.content = content

    @classmethod
    def get_successful_pdb_mock_request(*args, **kwargs):
        """Get a new successful mock for a PDB file request from PDB.

        :param args: positional arguments
        :param kwargs: named arguments
        :return: The new MockRequest.
        :rtype: MockRequest
        """
        with open(TestConfig.protein_file, 'r', encoding='utf-8') as file:
            return MockRequest(status_code=200, text=file.read())

    @classmethod
    def get_successful_density_mock_request(*args, **kwargs):
        """Get a new successful mock for a ElectronDensity file request from PDBe/EBI.

        :param args: positional arguments
        :param kwargs: named arguments
        :return: The new MockRequest.
        :rtype: MockRequest
        """
        with open(TestConfig.density_file, 'rb') as file:
            return MockRequest(status_code=200, content=file.read())

    @classmethod
    def get_failed_mock_request(*args, **kwargs):
        """Get a new failed mock for some request.

        :param args: positional arguments
        :param kwargs: named arguments
        :return: The new MockRequest.
        :rtype: MockRequest
        """
        return MockRequest(status_code=400)


class ExternalTests(PPlusTestCase):
    """External resources tests"""

    @override_settings(LOCAL_PDB_MIRROR_DIR=Path('test_files'))
    def test_fetch_by_pdb_code(self):
        """Test fetching structure by PDB code"""

        successful_mock = MockRequest.get_successful_pdb_mock_request()

        # test local fetch
        self.assertEqual(PDBResource.fetch(TestConfig.protein), successful_mock.text)

        # test external fetches
        with patch.object(PDBResource, '_external_request',
                          MockRequest.get_successful_pdb_mock_request):
            self.assertEqual(PDBResource.fetch('nonsense'), successful_mock.text)

        with patch.object(PDBResource, '_external_request',
                          MockRequest.get_failed_mock_request):
            self.assertRaises(RuntimeError, PDBResource.fetch, 'nonsense')

    @override_settings(LOCAL_DENSITY_MIRROR_DIR=Path('test_files'))
    def test_fetch_density_by_pdb_code(self):
        """Test fetching electron density file by PDB code"""

        successful_mock = MockRequest.get_successful_density_mock_request()

        # test local fetch
        self.assertEqual(DensityResource.fetch(TestConfig.protein), successful_mock.content)

        # test external fetches
        with patch.object(DensityResource, '_external_request',
                          MockRequest.get_successful_density_mock_request):
            self.assertEqual(DensityResource.fetch('nonsense'), successful_mock.content)

        with patch.object(DensityResource, '_external_request',
                          MockRequest.get_failed_mock_request):
            self.assertRaises(RuntimeError, DensityResource.fetch, 'nonsense')

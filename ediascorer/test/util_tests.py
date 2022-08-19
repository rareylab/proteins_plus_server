"""tests for ediascorer utility functions"""
from pathlib import Path
from django.test import override_settings

from proteins_plus.test.utils import PPlusTestCase
from molecule_handler.models import ElectronDensityMap
from .utils import create_test_edia_job


class UtilTests(PPlusTestCase):
    """Utility tests"""

    @override_settings(LOCAL_DENSITY_MIRROR_DIR=Path('test_files'))
    def test_get_density_file_with_pdb_code(self):
        """Test retrieving electron density file from server"""
        job = create_test_edia_job(density_filepath=None)
        self.assertIsNone(job.electron_density_map)
        job.electron_density_map = ElectronDensityMap.from_pdb_code(job.density_file_pdb_code)
        job.save()
        self.assertIsNotNone(job.electron_density_map)
        content = job.electron_density_map.file.read()
        self.assertGreater(len(content), 0)

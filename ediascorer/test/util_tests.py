"""tests for ediascorer utility functions"""
from proteins_plus.test.utils import PPlusTestCase
from ..tasks import get_density_file
from .utils import create_test_edia_job

class UtilTests(PPlusTestCase):
    """Utility tests"""
    def test_get_density_file_with_pdb_code(self):
        """Test retrieving electron density file from server"""
        job = create_test_edia_job(density_filepath=None)
        self.assertIsNone(job.electron_density_map)
        get_density_file(job)
        self.assertIsNotNone(job.electron_density_map)
        content = job.electron_density_map.file.read()
        self.assertGreater(len(content), 0)

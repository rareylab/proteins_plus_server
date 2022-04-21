"""tests for siena utility functions"""
from pathlib import Path
from proteins_plus.test.utils import PPlusTestCase, is_tool_available
from .config import TestConfig
from .utils import TmpSienaDB


class UtilTests(PPlusTestCase):
    """Utility tests"""

    def test_generate_siena_database(self):
        """Test generate siena database"""
        self.assertEqual(is_tool_available('generate_siena_database'), 64)
        protein_file_paths = [
            TestConfig.protein_file_4agm,
            TestConfig.protein_file_1a3e,
        ]

        # test database is not empty
        with TmpSienaDB(protein_file_paths) as database_file:
            self.assertTrue(database_file.is_file())
            self.assertGreater(database_file.stat().st_size, 0)

        # test log file has correct number of proteins written
        siena_db = TmpSienaDB(protein_file_paths)
        log_file_path = Path(siena_db.directory.name) / f'{database_file.name}.log'
        self.assertTrue(log_file_path.is_file())
        found = False
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                if 'New in db: 2' in line:
                    found = True
                    break
        siena_db.close()
        self.assertTrue(found)

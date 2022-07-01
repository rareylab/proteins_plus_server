"""Test for custom SIENA commands"""
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command, CommandError
from proteins_plus.test.utils import PPlusTestCase
from siena.test.config import TestConfig
from siena.test.utils import create_generate_siena_database_source_dir


class CommandsTests(PPlusTestCase):
    """Test for custom SIENA commands"""

    def test_generate_siena_database(self):
        """Test generate_siena_database command generates a SIENA database"""

        # test valid result for valid call
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)

            protein_file_paths = [TestConfig.protein_file_4agm, TestConfig.protein_file_1a3e]

            pdb_data_dir = dir_path / 'pdb_data'
            pdb_data_dir.mkdir()
            create_generate_siena_database_source_dir(
                destination_directory=pdb_data_dir,
                protein_file_paths=protein_file_paths
            )
            database_file = dir_path / 'siena.db'
            call_command('generate_siena_database',
                         '--database_filename', database_file.name,
                         '--source_dir', str(pdb_data_dir.resolve()),
                         '--destination_dir', str(dir_path.resolve()))

            # check that database file exists and is not empty
            self.assertTrue(database_file.is_file())
            self.assertGreater(database_file.stat().st_size, 0)

            # peak into log file to check if correct number of PDBs were added
            log_file_path = dir_path / f'{database_file.name}.log'
            self.assertTrue(log_file_path.is_file())
            found = False
            with open(log_file_path, 'r', encoding='utf8') as log_file:
                for line in log_file:
                    if 'New in db: 2' in line:
                        found = True
                        break
            self.assertTrue(found)

        # test invalid input
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)

            # test that no arguments raise error
            self.assertRaises(CommandError, call_command, 'generate_siena_database')

            # test that empty database name raises error
            self.assertRaises(CommandError, call_command, 'generate_siena_database',
                              '--database_filename', '',
                              '--source_dir', str(dir_path.resolve()),
                              '--destination_dir', str(dir_path.resolve()))

            # test that non-existing source_dir raises error
            self.assertRaises(CommandError, call_command, 'generate_siena_database',
                              '--database_filename', 'testDB',
                              '--source_dir', '/ThisIsA/VeryUnlikely/PathTo-Exist,isIt?42424242',
                              '--destination_dir', str(dir_path.resolve()))

            # test that non-existing destination_dir raises error
            self.assertRaises(CommandError, call_command, 'generate_siena_database',
                              '--database_filename', 'testDB',
                              '--source_dir', str(dir_path.resolve()),
                              '--destination_dir',
                              '/ThisIsA/VeryUnlikely/PathTo-Exist,isIt?42424242')

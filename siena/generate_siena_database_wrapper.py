"""A django model friendly wrapper around generate_siena_database binary"""
import logging
import subprocess
from django.conf import settings

logger = logging.getLogger(__name__)


class GenerateSienaDatabaseWrapper:  # pylint: disable=too-few-public-methods
    """A django model friendly wrapper around the generate_siena_database binary"""

    @staticmethod
    def execute_generate_siena_database(
            database_filename, source_dir, destination_dir, compressed=False):
        """Execute generate_siena_database to create a new SIENA-Site-Search database.

        :param database_filename: File name (not full path) of the new SIENA-Site-Search database.
        :type database_filename: str
        :param source_dir: Source directory of PDB files.
        :type source_dir: pathlib.Path
        :param destination_dir: Directory of resulting database and log files.
        :type destination_dir: pathlib.Path
        :param compressed: Flag to indicate whether PDB files are compressed.
        :param compressed: bool
        """

        args = [
            settings.BINARIES['generate_siena_database'],
            '-b', str(destination_dir / database_filename),
            '-d', str(source_dir.resolve()),
            '-f', str(0 if compressed else 1),
            '-o', str(destination_dir / f'{database_filename}.log')
        ]

        logger.info('Executing command line call: %s', " ".join(args))
        subprocess.check_call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

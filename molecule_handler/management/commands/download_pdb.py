"""Download PDB structure files"""
import logging
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError

from molecule_handler.settings import MoleculeHandlerSettings

logger = logging.getLogger(__name__)


def download_pdb_files(target_dir, pdb_file_format):
    """Downloads/Updates PDB mirror in target dir from RCSB PDB.

    This function implements the rsync call from the rsyncPDB.sh template script for
    for mirroring the PDB FTP archive using rsync. See
    https://www.rcsb.org/docs/programmatic-access/file-download-services

    :param target_dir: The target directory to store PDB files.
    :type target_dir: pathlib.Path
    :param pdb_file_format: Format of structure files. Can be 'pdb' or 'mmCIF'.
    :type pdb_file_format: str
    """

    # The following call implements the rsync call from the template script:
    # ${RSYNC} -rlpt -v -z --delete --port=$PORT ${SERVER}/data/structures/divided/pdb/ $MIRRORDIR
    # > $LOGFILE 2>/dev/null
    args = [
        'rsync',
        '-rlpt', '-v', '-z', '--delete',
        f'--port={MoleculeHandlerSettings.PDB_FTP_PORT}',
        f'{MoleculeHandlerSettings.PDB_FTP_SERVER}/data/structures/divided/{pdb_file_format}/',
        str(target_dir.resolve())
    ]
    logger.info('Executing command line call: %s', " ".join(args))
    subprocess.check_call(args)


class Command(BaseCommand):
    """Downloads/Updates local PDB mirror"""
    help = 'Downloads/Updates local PDB mirror. Only loads structure files (no meta info).'

    def add_arguments(self, parser):
        """Add commandline arguments

        :param parser: The argument parser
        :type parser: argparse.ArgumentParser
        """
        parser.add_argument('--target_dir', type=str, required=True,
                            help='Target dir for downloading files.')
        parser.add_argument('--format', type=str, default='pdb', choices=['pdb', 'mmCIF'],
                            help='PDB file format')

    def handle(self, *args, **options):
        """Handle command line call"""
        logging.info('Start downloading/updating PDB mirror')

        target_dir = Path(options['target_dir'])
        if not target_dir.is_dir():
            raise CommandError('target_dir does not exist')

        download_pdb_files(target_dir, options['format'])

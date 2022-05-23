"""Generate/Update a SIENA database"""
import logging
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from siena.generate_siena_database_wrapper import GenerateSienaDatabaseWrapper


class Command(BaseCommand):
    """Defines command to generate/update a SIENA database from the command line"""
    help = 'Generate/Update a SIENA database. This command wraps the' \
           'generate_siena_database executable.'

    def add_arguments(self, parser):
        """Add commandline arguments

        :param parser: The argument parser
        :type parser: argparse.ArgumentParser
        """

        parser.add_argument('--database_filename', type=str, required=True,
                            help='Name of the database file to generate.')
        parser.add_argument('--source_dir', type=str, required=True,
                            help='Source directory of PDB files that will be read recursively.')
        parser.add_argument('--destination_dir', type=str, required=True,
                            help='Directory to store the generated database. Final path to'
                                 'database will be <destination_dir>/<database_filename>')
        parser.add_argument('--compressed', action='store_true',
                            help='Whether PDB files to read are compressed (gzipped).')

    def handle(self, *args, **options):
        """Handles the command line call"""
        logging.info('Start generating/updating SIENA database')

        source_dir = Path(options['source_dir'])
        destination_dir = Path(options['destination_dir'])
        database_filename = options['database_filename']
        compressed = options['compressed']
        if not source_dir.is_dir():
            raise CommandError('source_dir does not exist')
        if not destination_dir.is_dir():
            raise CommandError('destination_dir does not exist')
        if len(database_filename) == 0:
            raise CommandError('Empty database name not allowed')

        GenerateSienaDatabaseWrapper.execute_generate_siena_database(database_filename, source_dir,
                                                                     destination_dir, compressed)

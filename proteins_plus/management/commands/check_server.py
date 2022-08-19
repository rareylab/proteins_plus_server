"""Check the server is running"""
import requests
import urllib.parse
from django.core.management.base import BaseCommand
from rest_framework import status
from molecule_handler.models import Ligand


class Command(BaseCommand):
    """Check the server is running"""
    help = 'Performs a number of checks to see whether the server is running correctly'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='URL the server is mounted on')

    @staticmethod
    def check_schema(base_url):
        """Check whether the OpenAPI schema can be retrieved

        :param base_url: URL to the mount point of the server
        :type base_url: str
        """
        schema_url = base_url + '/schema/'
        response = requests.get(schema_url)
        downloaded_schema = response.text
        with open('schema.yml') as schema_file:
            schema = schema_file.read()
        if downloaded_schema != schema:
            with open('downloaded_schema.yml', 'w') as downloaded_schema_file:
                downloaded_schema_file.write(downloaded_schema)
            raise RuntimeError('Downloaded schema and schema file are not the same')

    @staticmethod
    def check_api_call(base_url):
        """Check whether an API call works

        :param base_url: URL to the mount point of the server
        :type base_url: str
        """
        response = requests.post(base_url + '/molecule_handler/upload/', data={'pdb_code': '4agm'})
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise RuntimeError(f'Invalid API response:\n{response.text}')

    @staticmethod
    def check_static(base_url):
        """Check whether static assets can be retrieved

        :param base_url: URL to the mount point of the server
        :type base_url: str
        """
        ligand = Ligand.objects.exclude(image__isnull=True).exclude(image__exact='').first()

        if not ligand:
            # no ligand with image in the database not necessarily an error
            return
        image_url = urllib.parse.urljoin(base_url, ligand.image.url)
        response = requests.get(image_url)
        ligand_svg = response.text
        if '<svg' not in ligand_svg:
            with open('downloaded_ligand_image.svg', 'w') as ligand_image_file:
                ligand_image_file.write(ligand_svg)
            raise RuntimeError('Received invalid SVG image')

    def handle(self, *args, **options):
        self.check_schema(options['url'])
        self.check_api_call(options['url'])
        self.check_static(options['url'])

"""Clean molecule handler data"""
import logging
from django.core.management.base import BaseCommand
from proteins_plus.utils import clean_up_models
from molecule_handler.models import Protein, ElectronDensityMap, ProteinSite


class Command(BaseCommand):
    """Clean molecule handler data"""
    help = 'Cleans up molecule handler models if no non-stale jobs depend on them'

    def handle(self, *args, **options):
        logging.info('Start molecule handler clean up')
        clean_up_models(Protein)
        clean_up_models(ElectronDensityMap)

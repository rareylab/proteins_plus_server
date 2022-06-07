"""Specific settings of the SIENA app"""
import os


class SienaSettings:  # pylint: disable=too-few-public-methods
    """Holds all app specific settings"""
    SIENA_SEARCH_DB = os.environ['SIENA_SEARCH_DB'] if 'SIENA_SEARCH_DB' in os.environ \
                                                    else '/local/proteins_plus/static/siena_index_pdb.db'

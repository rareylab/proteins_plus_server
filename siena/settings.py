"""Specific settings of the SIENA app"""
import os


class SienaSettings:  # pylint: disable=too-few-public-methods
    """Holds all app specific settings"""
    # TODO what is the real path for that?
    SIENA_SEARCH_DB = os.environ['SIENA_SEARCH_DB'] if 'SIENA_SEARCH_DB' in os.environ \
                                                    else '/local/sieg/databases/siena_index_pdb.db'

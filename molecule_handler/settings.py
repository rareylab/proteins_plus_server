"""Specific settings of the molecule_handler app"""
import os


class MoleculeHandlerSettings:  # pylint: disable=too-few-public-methods
    """Holds all app specific settings"""

    # RCSB PDB server name
    PDB_FTP_SERVER = os.environ['PDB_FTP_SERVER'] if 'PDB_FTP_SERVER' in os.environ \
        else 'rsync.wwpdb.org::ftp'

    # port RCSB PDB server is using
    PDB_FTP_PORT = os.environ['PDB_FTP_PORT'] if 'PDB_FTP_PORT' in os.environ else '33444'

"""Handle request to local and external resources"""
import gzip
from abc import ABC, abstractmethod
from django.conf import settings

import requests


class Resource(ABC):
    """Abstract interface class for local/external resources

    We mainly use this class to enforce a common interface for handling local and external
    fetching universally and enable external requests mocking for testing while keeping high
    coverage.
    """

    @classmethod
    def fetch(cls, *args, **kwargs):
        """Interface method to fetch from a resource.

        It is first tried to fetch locally. If this fails an external fetch is attempted.

        :param args: positional arguments
        :param kwargs: named arguments
        :return: request result
        """
        req = cls._local_fetch(*args, **kwargs)
        if not req:
            req = cls._external_fetch(*args, **kwargs)
        return req

    @classmethod
    @abstractmethod
    def _local_fetch(cls, *args, **kwargs):
        """Abstract method that should implement a local fetch, i.e. to a local
        cache in the filesystem.

        :param args: positional arguments
        :param kwargs: named arguments
        :return: request result
        """
        pass

    @classmethod
    @abstractmethod
    def _external_fetch(cls, *args, **kwargs):
        """Abstract method that should implement an external fetch, i.e. to an API of
        some service through the internet.

        :param args: positional arguments
        :param kwargs: named arguments
        :return: request result
        """
        pass

    @classmethod
    @abstractmethod
    def _external_request(cls, *args, **kwargs):
        """Abstract method that should perform the actual external request. This is explicitly
        a separate method so external request can be mocked during testing. In this way we can
        keep a high test coverage.

        :param args: positional arguments
        :param kwargs: named arguments
        :return: request result
        """
        pass


class PDBResource(Resource):
    """Handles fetching PDB entries"""

    @classmethod
    def _local_fetch(cls, pdb_code):
        """Tries to read the PDB-file corresponding to pdb_code from disk.

        :param pdb_code: The PDB-code.
        :return: The file string of the PDB file or None on failure.
        """
        if pdb_code is None:
            return None
        local_path = settings.LOCAL_PDB_MIRROR_DIR / f'pdb{pdb_code.lower()}.ent.gz'
        if not local_path.is_file():
            return None
        # read PDB file from local mirror
        with gzip.open(local_path, 'rt') as pdb_file:
            file_string = pdb_file.read()
        return file_string

    @classmethod
    def _external_fetch(cls, pdb_code):
        """Tries to fetch the PDB entry corresponding to pdb_code from the PDB API.

        :param pdb_code: The PDB-code.
        :return: The file string of the PDB file.
        :raises: RuntimeError if request fails.
        """
        file_type = 'pdb'
        # try to fetch PDB file from PDB server
        url = f'{settings.URLS["pdb_files"]}{pdb_code}.{file_type}'
        req = cls._external_request(url)
        if req.status_code != 200:
            raise RuntimeError(
                f"Error while retrieving pdb file with pdb code {pdb_code}\n" +
                f"Request: GET {url}\n" +
                f"Response: \n{req.text}")
        file_string = req.text
        return file_string

    @classmethod
    def _external_request(cls, url):
        """Makes a get request to url and returns the result.

        :param url: The URL.
        :return: The response.
        """
        return requests.get(url)


class DensityResource(Resource):
    """Handles fetching density files"""

    @classmethod
    def _local_fetch(cls, pdb_code):
        """Tries to read the density file corresponding to pdb_code from disk.

        :param pdb_code: The PDB-code.
        :return: The file string of the PDB file or None on failure.
        """
        if pdb_code is None:
            return None
        local_path = settings.LOCAL_DENSITY_MIRROR_DIR / f'{pdb_code.lower()}.ccp4'
        if not local_path.is_file():
            return None
        # read density file from local mirror
        with open(local_path, 'rb') as density_file:
            file_bytes = density_file.read()
        return file_bytes

    @classmethod
    def _external_fetch(cls, pdb_code):
        """Fetch electron density file from server and return it as bytearray.

        :param pdb_code: pdb code of protein
        :type pdb_code: str
        :return: Density in ccp4 format as bytearray or None.
        :rtype: bytearray or None if failure
        """
        url = f'{settings.URLS["density_files"]}{pdb_code}.ccp4'
        req = cls._external_request(url)
        if req.status_code != 200:
            raise RuntimeError(
                f"Error while retrieving ccp4 file with pdb code {pdb_code}\n" +
                f"Request: GET {url}\n" +
                f"Response: \n{req.text}")
        return bytearray(req.content)

    @classmethod
    def _external_request(cls, url):
        """Makes a get request to url and returns the result.

        :param url: The URL.
        :return: The response.
        """
        return requests.get(url)

"""Functionality to consistently validate molecular user input"""
from pathlib import Path
import re
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from molecule_handler.models import Protein

PDB_CODE_PATTERN = re.compile(r'^[0-9][a-zA-Z0-9]{3}$')
UNIPROT_PATTERN = re.compile(
    r'^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$')

PROTEIN_FILE_FORMATS = ('.pdb',)
LIGAND_FILE_FORMATS = ('.sdf',)
ELECTRON_DENSITY_FILE_FORMATS = ('.ccp4',)


class MoleculeInputValidator:
    """Configurable class for validating molecular input

    The purpose of this class is to centralize the validation and
    error messages of molecular data to guarantee a consistent
    handling of molecule input over all apps.
    """

    def __init__(self, data, protein_file_formats=PROTEIN_FILE_FORMATS,
                 ligand_file_formats=LIGAND_FILE_FORMATS,
                 electron_density_file_formats=ELECTRON_DENSITY_FILE_FORMATS):
        """Construct a new validator

        :param data: key/value based to check data
        :param protein_file_formats: Allowed protein file formats
        :param ligand_file_formats: Allowed ligand file formats
        :param electron_density_file_formats: Allowed electron density file formats
        """
        self.data = data
        self.protein_file_formats = protein_file_formats
        self.ligand_file_formats = ligand_file_formats
        self.electron_density_file_formats = electron_density_file_formats

    def has_valid_protein_id(self):
        """Checks if data contains a valid database protein id

         :raises NotFound: If no Protein matches the given protein id
         :return: true if a valid protein_id is in data, false otherwise
         """
        if 'protein_id' not in self.data or self.data['protein_id'] is None:
            return False
        try:
            Protein.objects.get(id=self.data['protein_id'])
        except Protein.DoesNotExist:
            raise NotFound(
                detail='Protein with given protein id does not exist'
            ) from None
        return True

    def has_valid_pdb_code(self):
        """Checks if data contains a valid pdb code

        :raises serializers.ValidationError: If an invalid pdb code was provided
        :return: true if a valid pdb_code is in data, false otherwise
        """
        if 'pdb_code' not in self.data or self.data['pdb_code'] is None:
            return False
        if not PDB_CODE_PATTERN.match(self.data['pdb_code']):
            raise serializers.ValidationError(
                'Invalid pdb code was provided.'
            )
        return True

    def has_valid_uniprot_code(self):
        """Checks if data contains a valid uniprot code

        :raises serializers.ValidationError: If an invalid uniprot code was provided
        :return: true if a valid uniprot_code is in data, false otherwise
        """
        if 'uniprot_code' not in self.data or self.data['uniprot_code'] is None:
            return False
        if not UNIPROT_PATTERN.match(self.data['uniprot_code']):
            raise serializers.ValidationError(
                'Invalid uniprot code was provided.'
            )
        return True

    def has_valid_protein_file(self):
        """Checks if data contains a valid protein file

        :raises serializers.ValidationError: If the protein file has the wrong filetype
        :return: true if a valid protein_file is in data, false otherwise
        """
        return self._has_valid_file('protein_file', self.protein_file_formats)

    def has_valid_ligand_file(self):
        """Checks if data contains a valid ligand file

        :raises serializers.ValidationError: If the ligand file has the wrong filetype
        :return: true if a valid ligand_file is in data, false otherwise
        """
        return self._has_valid_file('ligand_file', self.ligand_file_formats)

    def has_valid_electron_density_map(self):
        """Checks if data contains a valid electron density file

        :raises serializers.ValidationError: If the electron density file has the wrong filetype
        :return: true if a valid electron_density_map is in data, false otherwise
        """
        return self._has_valid_file('electron_density_map', self.electron_density_file_formats)

    def _has_valid_file(self, key, valid_extensions):
        """Checks if data contains a field named 'key' with a valid file extension.

        :raises serializers.ValidationError: If the file has the wrong filetype
        :return: true if a valid field with the 'key' is in data, false otherwise
        """
        if key not in self.data or self.data[key] is None:
            return False
        ext = Path(self.data[key].name).suffixes[-1]
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f'Bad {key} format. Allowed formats: {valid_extensions}.'
            )
        return True

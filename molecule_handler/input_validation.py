"""Functionality to consistently validate molecular user input"""
from pathlib import Path
import re
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from molecule_handler.models import Protein, ProteinSite, Ligand

PDB_CODE_PATTERN = re.compile(r'^[0-9][a-zA-Z0-9]{3}$')
UNIPROT_PATTERN = re.compile(
    r'^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$')
# Parse residue ID in PDB files. Limit iCodes to 3 letters.
RESIDUE_PDB_POSITION_PATTERN = re.compile(r'^-?[0-9]+[a-zA-Z]{0,3}$')

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
        :type data: dict
        :param protein_file_formats: Allowed protein file formats
        :type protein_file_formats: tuple
        :param ligand_file_formats: Allowed ligand file formats
        :type ligand_file_formats: tuple
        :param electron_density_file_formats: Allowed electron density file formats
        :type electron_density_file_formats: tuple
        """
        self.data = data
        self.protein_file_formats = protein_file_formats
        self.ligand_file_formats = ligand_file_formats
        self.electron_density_file_formats = electron_density_file_formats

    def has_valid_protein_id(self):
        """Checks if data contains a valid database protein id

         :raises NotFound: If no Protein matches the given protein id
         :return: true if a valid protein_id is in data, false otherwise
         :rtype: bool
         """
        return self._check_valid_id('protein_id', Protein)

    def has_valid_ligand_id(self):
        """Checks if data contains a valid database ligand id

         :raises NotFound: If no Ligand matches the given ligand id
         :return: true if a valid ligand_id is in data, false otherwise
         :rtype: bool
         """
        return self._check_valid_id('ligand_id', Ligand)

    def has_valid_protein_site_id(self):
        """Checks if data contains a valid database protein site id

         :raises NotFound: If no ProteinSite matches the given protein site id
         :return: true if a valid protein site id is in data, false otherwise
         :rtype: bool
         """
        return self._check_valid_id('protein_site_id', ProteinSite)

    def _check_valid_id(self, data_key, model_type):
        if data_key not in self.data or self.data[data_key] is None:
            return False
        try:
            model_type.objects.get(id=self.data[data_key])
        except model_type.DoesNotExist:
            raise NotFound(
                detail=f'{model_type.__name__} with given id does not exist'
            ) from None
        return True

    def has_valid_pdb_code(self):
        """Checks if data contains a valid pdb code

        :raises serializers.ValidationError: If an invalid pdb code was provided
        :return: true if a valid pdb_code is in data, false otherwise
        :rtype: bool
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
        :rtype: bool
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
        :rtype: bool
        """
        return self._has_valid_file('protein_file', self.protein_file_formats)

    def has_valid_ligand_file(self):
        """Checks if data contains a valid ligand file

        :raises serializers.ValidationError: If the ligand file has the wrong filetype
        :return: true if a valid ligand_file is in data, false otherwise
        :rtype: bool
        """
        return self._has_valid_file('ligand_file', self.ligand_file_formats)

    def has_valid_electron_density_map(self):
        """Checks if data contains a valid electron density file

        :raises serializers.ValidationError: If the electron density file has the wrong filetype
        :return: true if a valid electron_density_map is in data, false otherwise
        :rtype: bool
        """
        return self._has_valid_file('electron_density_map', self.electron_density_file_formats)

    def _has_valid_file(self, key, valid_extensions):
        """Checks if data contains a field named 'key' with a valid file extension.

        :raises serializers.ValidationError: If the file has the wrong filetype
        :return: true if a valid field with the 'key' is in data, false otherwise
        :rtype: bool
        """
        if key not in self.data or self.data[key] is None:
            return False
        path = Path(self.data[key].name)
        if len(path.suffixes) == 0 or path.suffixes[-1] not in valid_extensions:
            raise serializers.ValidationError(
                f'Bad {key} format. Allowed formats: {valid_extensions}.'
            )
        return True

    def has_valid_protein_site_json(self):
        """Check if a valid JSON dict describing a protein site is provided in the data.

        :raises serializers.ValidationError: If an invalid JSON was provided
        :return: true if a valid protein site description was provided, false otherwise
        :rtype: bool
        """
        if 'protein_site_json' not in self.data or self.data['protein_site_json'] is None:
            return False
        self._has_valid_residue_ids(self.data['protein_site_json'])
        return True

    @staticmethod
    def _has_valid_residue_ids(json_data):
        """Check if a valid JSON dict describing residues of a protein site is provided.

        :raises serializers.ValidationError: If an invalid JSON was provided
        """
        if 'residue_ids' not in json_data:
            raise serializers.ValidationError(
                'Bad input data for protein site specification: Supply \'residue_ids\' field.'
            )
        residue_ids_list = json_data['residue_ids']
        try:
            iter(residue_ids_list)
        except TypeError:
            raise serializers.ValidationError(
                'Residue list is not in an iterable format.'
            ) from None

        seen = set()
        for residue_id_data in residue_ids_list:
            if 'name' not in residue_id_data or len(residue_id_data['name']) != 3:
                raise serializers.ValidationError('Invalid residue specification: Bad name')
            if 'position' not in residue_id_data or not RESIDUE_PDB_POSITION_PATTERN.match(
                    residue_id_data['position']):
                raise serializers.ValidationError('Invalid residue specification: Bad position')
            if 'chain' not in residue_id_data or len(residue_id_data['chain']) < 1 \
                    or len(residue_id_data['chain']) > 2:
                raise serializers.ValidationError('Invalid residue specification: Bad chain')
            res_str = f"{residue_id_data['name']}_" \
                      f"{residue_id_data['position']}_{residue_id_data['chain']}"
            if res_str in seen:
                raise serializers.ValidationError(
                    'Invalid residue specification: Duplicate residues in residue_ids list')
            seen.add(res_str)

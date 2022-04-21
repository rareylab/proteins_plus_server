"""siena model serializers for django rest framework"""

from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.input_validation import MoleculeInputValidator

from .models import SienaJob, SienaInfo


class SienaJobSerializer(ProteinsPlusJobSerializer):
    """Serializer for the SienaJob model"""

    class Meta(ProteinsPlusJobSerializer.Meta):
        model = SienaJob
        fields = ProteinsPlusJobSerializer.Meta.fields + [
            'input_protein',
            'input_ligand',
            'input_site',
            'output_info',
            'output_proteins'
        ]


class SienaInfoSerializer(serializers.ModelSerializer):
    """Serializer for the SienaInfo model"""

    class Meta:
        model = SienaInfo
        fields = ['id', 'statistic', 'alignment', 'parent_siena_job']


class SienaSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """Serializer for the Siena job submission data"""
    protein_id = serializers.UUIDField(required=False, default=None)
    protein_file = serializers.FileField(required=False, default=None)
    ligand_id = serializers.UUIDField(required=False, default=None)
    ligand_file = serializers.FileField(required=False, default=None)
    protein_site_id = serializers.UUIDField(required=False, default=None)
    protein_site_json = serializers.JSONField(required=False, default=None)

    def validate(self, data):  # pylint: disable=arguments-renamed
        """Data validation

        :param data: Job submission data
        :type data: collections.OrderedDict
        :raises serializers.ValidationError: If neither pdb code or pdb file were provided
        :raises serializers.ValidationError: If neither electron density file nor pdb code
                                            was provided
        :return: Validated data
        :rtype data: collections.OrderedDict
        """
        validator = MoleculeInputValidator(data)
        has_valid_protein_id = validator.has_valid_protein_id()
        has_valid_protein_file = validator.has_valid_protein_file()
        has_valid_ligand_id = validator.has_valid_ligand_id()
        has_valid_ligand_file = validator.has_valid_ligand_file()
        has_valid_protein_site_id = validator.has_valid_protein_site_id()
        has_valid_protein_site_json = validator.has_valid_protein_site_json()

        has_protein_site = has_valid_protein_site_id or has_valid_protein_site_json
        has_ligand = has_valid_ligand_id or has_valid_ligand_file

        if not has_protein_site and not has_ligand:
            raise serializers.ValidationError(
                'Neither valid protein site nor ligand were provided.')

        if not has_valid_protein_id and not has_valid_protein_file:
            raise serializers.ValidationError(
                'Provide either a protein id or protein file. Not both.')
        if has_valid_protein_id and has_valid_protein_file:
            raise serializers.ValidationError(
                'Provide either a protein id or protein file. Not both.')
        if has_valid_ligand_id and has_valid_ligand_file:
            raise serializers.ValidationError(
                'Provide either a ligand id or ligand file. Not both.')
        if has_valid_protein_site_id and has_valid_protein_site_json:
            raise serializers.ValidationError(
                'Provide either a protein site id or protein site JSON. Not both.')
        if has_protein_site and has_ligand:
            raise serializers.ValidationError(
                'Provide the binding site definition either as protein site or ligand. Not both.')

        if has_valid_protein_id:
            # if the query protein is already in the database we do not accept ligand files, but
            # only protein sites (in any form) or ligands from the database.
            if not has_protein_site and not has_valid_ligand_id:
                raise serializers.ValidationError(
                    'Provide a site or ligand id when using a protein id as input. Ligand files are'
                    ' not allowed.')
        return data

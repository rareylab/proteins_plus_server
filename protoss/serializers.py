"""Protoss model serializers"""
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.input_validation import MoleculeInputValidator
from .models import ProtossJob


class ProtossJobSerializer(ProteinsPlusJobSerializer):
    """Serializer for ProtossJob model"""

    class Meta(ProteinsPlusJobSerializer.Meta):
        model = ProtossJob
        fields = ProteinsPlusJobSerializer.Meta.fields + ['input_protein', 'input_ligand', 'output_protein']


class ProtossSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """Serializer for the Protoss job submission data"""
    protein_id = serializers.UUIDField(required=False, default=None)
    protein_file = serializers.FileField(required=False, default=None)
    ligand_file = serializers.FileField(required=False, default=None)

    def validate(self, data):  # pylint: disable=arguments-renamed
        """Data validation

        :param data: Job submission data
        :raises serializers.ValidationError: If neither pdb code or pdb file were provided
        :return: Validated data
        """
        validator = MoleculeInputValidator(data)
        if not validator.has_valid_protein_id() and not validator.has_valid_protein_file():
            raise serializers.ValidationError('Neither protein id nor protein file were provided.')
        validator.has_valid_ligand_file()
        return data

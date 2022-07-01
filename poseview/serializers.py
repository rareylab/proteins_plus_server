"""Poseview model serializers"""
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.input_validation import MoleculeInputValidator
from .models import PoseviewJob


class PoseviewJobSerializer(ProteinsPlusJobSerializer):
    """PoseView job data"""

    class Meta:
        model = PoseviewJob
        fields = ProteinsPlusJobSerializer.Meta.fields + [
            'input_protein',
            'input_ligand',
            'image'
        ]


class PoseviewJobSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """PoseView job submission data"""
    protein_id = serializers.UUIDField(required=False, default=None)
    protein_file = serializers.FileField(required=False, default=None)
    ligand_id = serializers.UUIDField(required=False, default=None)
    ligand_file = serializers.FileField(required=False, default=None)

    def validate(self, data):  # pylint: disable=arguments-renamed
        """Validate Poseview submission data

        :param data: data to validate
        :type data: collections.OrderedDict
        :raises serializers.ValidationError: If neither files nor model IDs for ligand and protein
        were provided
        :return: Validated data
        :rtype: collections.OrderedDict
        """
        validator = MoleculeInputValidator(data)
        if not validator.has_valid_protein_id() and not validator.has_valid_protein_file():
            raise serializers.ValidationError('Neither protein id nor protein file were provided.')
        if not validator.has_valid_protein_id() and not validator.has_valid_ligand_file():
            raise serializers.ValidationError('Neither ligand id nor ligand file were provided.')
        return data

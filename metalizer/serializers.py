"""Metalizer model serializers"""
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.input_validation import MoleculeInputValidator

from .models import MetalizerJob, MetalizerInfo


class MetalizerJobSerializer(ProteinsPlusJobSerializer):
    """Serializer for the MetalizerJob model"""

    class Meta:
        model = MetalizerJob
        fields = ProteinsPlusJobSerializer.Meta.fields + [
            'input_protein',
            'residue_id',
            'chain_id',
            'name',
            'distance_threshold',
            'output_protein',
            'metalizer_info'
        ]


class MetalizerInfoSerializer(serializers.ModelSerializer):
    """Serializer for the MetalizerInfo model"""

    class Meta:
        model = MetalizerInfo
        fields = ['id', 'info', 'parent_metalizer_job']


class MetalizerJobSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """Serializer for the Metalizer job submission data"""
    protein_id = serializers.UUIDField(required=False, default=None)
    protein_file = serializers.FileField(required=False, default=None)
    residue_id = serializers.IntegerField()
    chain_id = serializers.CharField(max_length=2)
    name = serializers.CharField(max_length=2)
    distance_threshold = serializers.FloatField()

    def validate(self, data):  # pylint: disable=arguments-renamed
        """Validate Metalizer submission data

        :param data: data to validate
        :raises serializers.ValidationError: If neither pdb code or pdb file were provided
        :return: Validated data
        """
        validator = MoleculeInputValidator(data)
        if not validator.has_valid_protein_id() and not validator.has_valid_protein_file():
            raise serializers.ValidationError('Neither protein id nor protein file were provided.')
        return data

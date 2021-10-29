"""Protoss model serializers"""
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.models import Protein
from .models import ProtossJob

class ProtossJobSerializer(ProteinsPlusJobSerializer):
    """Serializer for ProtossJob model"""
    class Meta(ProteinsPlusJobSerializer.Meta):
        model = ProtossJob
        fields = ProteinsPlusJobSerializer.Meta.fields + ['input_protein', 'output_protein']

class ProtossSubmitSerializer(ProteinsPlusJobSubmitSerializer): # pylint: disable=abstract-method
    """Serializer for the Protoss job submission data"""
    protein_id = serializers.UUIDField(required=True)

    def validate(self, data): # pylint: disable=arguments-renamed
        """Data validation

        :param data: Job submission data
        :raises NotFound: If no Protein matches the given protein id
        :return: Validated data
        """
        try:
            _ = Protein.objects.get(id=data['protein_id'])
        except Protein.DoesNotExist:
            raise NotFound(detail="Protein object with given protein id does not exist") from None
        return data

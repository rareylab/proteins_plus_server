"""Protoss model serializers"""
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.models import Protein
from molecule_handler.validation import valid_protein_extension, valid_ligand_extension
from .models import ProtossJob


class ProtossJobSerializer(ProteinsPlusJobSerializer):
    """Serializer for ProtossJob model"""

    class Meta(ProteinsPlusJobSerializer.Meta):
        model = ProtossJob
        fields = ProteinsPlusJobSerializer.Meta.fields + ['input_protein', 'output_protein']


class ProtossSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """Serializer for the Protoss job submission data"""
    protein_id = serializers.UUIDField(required=False, default=None)
    protein_file = serializers.FileField(required=False, default=None)
    ligand_file = serializers.FileField(required=False, default=None)

    def validate(self, data):  # pylint: disable=arguments-renamed
        """Data validation

        :param data: Job submission data
        :raises NotFound: If no Protein matches the given protein id
        :raises ValidationError: If file extensions are invalid
        :return: Validated data
        """
        if data['protein_id']:
            try:
                _ = Protein.objects.get(id=data['protein_id'])
            except Protein.DoesNotExist:
                raise NotFound(detail='Protein object with given protein id does not exist') from None
        elif data['protein_file']:
            if not valid_protein_extension(data['protein_file']):
                raise serializers.ValidationError(
                    'For proteins only pdb files are supported at the moment.'
                )
            if data['ligand_file'] is not None:
                if not valid_ligand_extension(data['ligand_file']):
                    raise serializers.ValidationError(
                        'For ligands only sdf files are supported at the moment.'
                    )
        else:
            raise serializers.ValidationError('Neither protein id nor protein file were provided.')
        return data

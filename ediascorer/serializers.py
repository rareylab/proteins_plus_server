"""ediascorer model serializers for django rest framework"""
import re
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.models import Protein
from .models import EdiaJob, AtomScores

class EdiaJobSerializer(ProteinsPlusJobSerializer):
    """Serializer for the EdiaJob model"""

    class Meta(ProteinsPlusJobSerializer.Meta):
        model = EdiaJob
        fields = ProteinsPlusJobSerializer.Meta.fields + ['input_protein', 'density_file_pdb_code',
                'electron_density_map', 'atom_scores', 'output_protein']

class AtomScoresSerializer(serializers.ModelSerializer):
    """Serializer for the AtomScores model"""

    class Meta:
        model = AtomScores
        fields = ['id', 'scores', 'edia_job']

class EdiascorerSubmitSerializer(ProteinsPlusJobSubmitSerializer): # pylint: disable=abstract-method
    """Serializer for the Protoss job submission data"""
    protein_id = serializers.UUIDField(required=True)
    pdb_code = serializers.CharField(min_length=4, max_length=4, default=None)
    electron_density_map = serializers.FileField(default=None)

    def validate(self, data): # pylint: disable=arguments-renamed
        """Data validation

        :param data: Job submission data
        :raises NotFound: If no Protein matches the given protein id
        :raises serializers.ValidationError: If neither electron density file nor pdb code
                                            was provided
        :raises serializers.ValidationError: If an invalid pdb code was provided
        :return: Validated data
        """
        protein = None
        try:
            protein = Protein.objects.get(id=data['protein_id'])
        except Protein.DoesNotExist:
            raise NotFound(
                detail='Protein with given protein id does not exist'
            ) from None
        if data['electron_density_map'] is None and data['pdb_code'] is None and \
            protein.pdb_code is None:
            raise serializers.ValidationError(
                'Neither electron density map nor pdb code were given.'
                )
        if data['pdb_code'] is not None:
            pdb_pattern = re.compile('[0-9][a-zA-Z0-9]{3}')
            if not pdb_pattern.match(data['pdb_code']):
                raise serializers.ValidationError(
                    'Invalid pdb code was provided.'
                    )
        return data

"""ediascorer model serializers for django rest framework"""
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.models import Protein
from molecule_handler.input_validation import MoleculeInputValidator

from .models import EdiaJob, EdiaScores


class EdiaJobSerializer(ProteinsPlusJobSerializer):
    """Serializer for the EdiaJob model"""

    class Meta(ProteinsPlusJobSerializer.Meta):
        model = EdiaJob
        fields = ProteinsPlusJobSerializer.Meta.fields + [
            'input_protein',
            'density_file_pdb_code',
            'electron_density_map',
            'edia_scores',
            'output_protein'
        ]


class EdiaScoresSerializer(serializers.ModelSerializer):
    """EDIA scores data"""

    class Meta:
        model = EdiaScores
        fields = ['id', 'atom_scores', 'structure_scores', 'parent_edia_job']


class EdiascorerSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """Serializer for the Protoss job submission data"""
    protein_id = serializers.UUIDField(required=False, default=None)
    protein_file = serializers.FileField(required=False, default=None)
    ligand_file = serializers.FileField(required=False, default=None)
    pdb_code = serializers.CharField(min_length=4, max_length=4, default=None)
    electron_density_map = serializers.FileField(default=None)

    def validate(self, data):  # pylint: disable=arguments-renamed
        """Data validation

        :param data: Job submission data
        :raises serializers.ValidationError: If neither pdb code or pdb file were provided
        :raises serializers.ValidationError: If neither electron density file nor pdb code
                                            was provided
        :return: Validated data
        """
        validator = MoleculeInputValidator(data)
        has_protein_id = validator.has_valid_protein_id()
        has_protein_file = validator.has_valid_protein_file()
        validator.has_valid_ligand_file()
        has_density_file = validator.has_valid_electron_density_map()
        has_pdb_code = validator.has_valid_pdb_code()

        if not has_protein_id and not has_protein_file:
            raise serializers.ValidationError('Neither protein id nor protein file were provided.')
        if has_protein_id:
            protein = Protein.objects.get(id=data['protein_id'])
            if not has_density_file and not has_pdb_code and protein.pdb_code is None:
                raise serializers.ValidationError(
                    'Neither electron density map nor pdb code were given.'
                )
        return data

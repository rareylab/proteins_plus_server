"""structureprofiler model serializers for django rest framework"""
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSubmitSerializer, ProteinsPlusJobSerializer
from molecule_handler.input_validation import MoleculeInputValidator

from .models import StructureProfilerJob, StructureProfilerOutput


class StructureProfilerJobSerializer(ProteinsPlusJobSerializer):
    """ StructureProfiler job data """

    class Meta(ProteinsPlusJobSerializer.Meta):
        model = StructureProfilerJob
        fields = ProteinsPlusJobSerializer.Meta.fields + [
            'input_protein',
            'input_ligand',
            'density_file_pdb_code',
            'electron_density_map',
            'output_data'
        ]


class StructureProfilerOutputSerializer(serializers.ModelSerializer):
    """ StructureProfiler output data"""

    class Meta:
        model = StructureProfilerOutput
        fields = ['id', 'output_data', 'parent_structureprofiler_job']


class StructureProfilerSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """ StructureProfiler job submission data"""
    protein_id = serializers.UUIDField(required=False, default=None)
    protein_file = serializers.FileField(required=False, default=None)
    pdb_code = serializers.CharField(min_length=4, max_length=4, default=None, required=False)
    electron_density_map = serializers.FileField(default=None, required=False)
    ligand_file = serializers.FileField(required=False, default=None)

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
        if not has_protein_id and not has_protein_file:
            raise serializers.ValidationError('Neither protein Id nor protein file were provided.')

        validator.has_valid_pdb_code()
        validator.has_valid_electron_density_map()
        validator.has_valid_ligand_file()

        return data

"""DoGSite model serializers"""
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.input_validation import MoleculeInputValidator

from .models import DoGSiteJob, DoGSiteInfo


class DoGSiteJobSerializer(ProteinsPlusJobSerializer):
    """DoGSite job data"""

    class Meta:
        model = DoGSiteJob
        fields = ProteinsPlusJobSerializer.Meta.fields + [
            'input_protein',
            'input_ligand',
            'chain_id',
            'calc_subpockets',
            'ligand_bias',
            'output_pockets',
            'output_densities',
            'dogsite_info'
        ]


class DoGSiteInfoSerializer(serializers.ModelSerializer):
    """DoGSite result info data"""

    class Meta:
        model = DoGSiteInfo
        fields = ['id', 'info', 'parent_dogsite_job']


class DoGSiteJobSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """DoGSite job submission data"""

    protein_id = serializers.UUIDField(required=False, default=None)
    protein_file = serializers.FileField(required=False, default=None)
    ligand_id = serializers.UUIDField(required=False, default=None)
    ligand_file = serializers.FileField(required=False, default=None)
    chain_id = serializers.CharField(required=False, max_length=2, default=None)
    calc_subpockets = serializers.BooleanField()
    ligand_bias = serializers.BooleanField()

    def validate(self, data):  # pylint: disable=arguments-renamed
        """Validate DoGSite submission data

        :param data: data to validate
        :type data: collections.OrderedDict
        :raises serializers.ValidationError: If neither pdb code or pdb file were provided
        :return: Validated data
        :rtype: collections.OrderedDict
        """
        validator = MoleculeInputValidator(data)
        has_valid_protein_id = validator.has_valid_protein_id()
        has_valid_protein_file = validator.has_valid_protein_file()
        has_valid_ligand_id = validator.has_valid_ligand_id()
        has_valid_ligand_file = validator.has_valid_ligand_file()

        if has_valid_protein_id and has_valid_protein_file:
            raise serializers.ValidationError(
                'Provide either a protein id or protein file. Not both.')
        if has_valid_ligand_id and has_valid_ligand_file:
            raise serializers.ValidationError(
                'Provide either a ligand id or ligand file. Not both.')

        if not has_valid_protein_id and not has_valid_protein_file:
            raise serializers.ValidationError('Neither protein id nor protein file were provided.')
        return data

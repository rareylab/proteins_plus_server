"""molecule_handler model serializers for django rest framework"""
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from .models import Protein, Ligand, ProteinSite, ElectronDensityMap, PreprocessorJob, \
    PreprocessorJobData
from .input_validation import MoleculeInputValidator


class ProteinSerializer(serializers.ModelSerializer):
    """Protein data"""

    class Meta:
        model = Protein
        fields = [
            'id',
            'name',
            'pdb_code',
            'uniprot_code',
            'file_type',
            'ligand_set',
            'file_string',
            'date_created',
            'date_last_accessed'
        ]


class LigandSerializer(serializers.ModelSerializer):
    """Ligand data

    Image is in SVG format.
    """

    class Meta:
        model = Ligand
        fields = ['id', 'name', 'protein', 'file_type', 'file_string', 'image']


class ProteinSiteSerializer(serializers.ModelSerializer):
    """Serializer for the Protein model"""

    class Meta:
        model = ProteinSite
        fields = ['id', 'protein', 'site_description']


class ElectronDensityMapSerializer(serializers.ModelSerializer):
    """Electron density map data

    Electron density is in CCP4 format.
    """

    class Meta:
        model = ElectronDensityMap
        fields = ['id', 'file', 'date_created', 'date_last_accessed']


class PreprocessorJobDataSerializer(serializers.ModelSerializer):
    """Preprocessor job data"""

    class Meta:
        model = PreprocessorJobData
        fields = [
            'parent_preprocessor_job', 'input_protein_string', 'input_protein_file_type',
            'input_ligand_string', 'input_ligand_file_type'
        ]


class PreprocessorJobSerializer(ProteinsPlusJobSerializer):
    """Preprocessor job data"""

    class Meta(ProteinsPlusJobSerializer.Meta):
        model = PreprocessorJob
        fields = ProteinsPlusJobSerializer.Meta.fields + [
            'pdb_code',
            'uniprot_code',
            'input_data',
            'output_protein'
        ]


class UploadSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """Upload data"""
    pdb_code = serializers.CharField(min_length=4, max_length=4, default=None)
    uniprot_code = serializers.CharField(min_length=6, max_length=10, default=None)
    protein_file = serializers.FileField(default=None)
    ligand_file = serializers.FileField(default=None)

    def validate(self, data):  # pylint: disable=arguments-renamed
        """Data validation

        :param data: Upload data
        :raises serializers.ValidationError: If neither pdb code or pdb file were provided
        :return: Validated data
        """
        validator = MoleculeInputValidator(data)
        if not validator.has_valid_pdb_code() and not validator.has_valid_protein_file() \
                and not validator.has_valid_uniprot_code():
            raise serializers.ValidationError('Neither pdb code not pdb file were provided.')

        validator.has_valid_ligand_file()
        return data

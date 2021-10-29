"""molecule_handler model serializers for django rest framework"""
import os
import re
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from .models import Protein, Ligand, ElectronDensityMap, PreprocessorJob

class ProteinSerializer(serializers.ModelSerializer):
    """Serializer for the Protein model"""
    class Meta:
        model = Protein
        fields = ['id', 'name', 'pdb_code', 'file_type',
                'ligand_set', 'parent_protoss_job', 'child_protoss_job_set',
                'parent_edia_job', 'child_edia_job_set',
                'file_string', 'date_created', 'date_last_accessed']

class LigandSerializer(serializers.ModelSerializer):
    """Serializer for the Ligand model"""
    class Meta:
        model = Ligand
        fields = ['id', 'name', 'protein', 'file_type', 'file_string', 'image']

class ElectronDensityMapSerializer(serializers.ModelSerializer):
    """Serializer for the ElectronDensityMap model"""

    class Meta:
        model = ElectronDensityMap
        fields = ['id', 'file', 'edia_job']

class PreprocessorJobSerializer(ProteinsPlusJobSerializer):
    """Serializer for the PreprocessorJob model"""
    class Meta(ProteinsPlusJobSerializer.Meta):
        model = PreprocessorJob
        fields = ProteinsPlusJobSerializer.Meta.fields + ['protein_name', 'pdb_code',
                'output_protein', 'protein_string', 'ligand_string']

class UploadSerializer(ProteinsPlusJobSubmitSerializer): # pylint: disable=abstract-method
    """Serializer for Protein upload data"""
    pdb_code = serializers.CharField(min_length=4, max_length=4, default=None)
    uniprot_code = serializers.CharField(min_length=6, max_length=10, default=None)
    protein_file = serializers.FileField(default=None)
    ligand_file = serializers.FileField(default=None)

    def validate(self, data): # pylint: disable=arguments-renamed
        """Data validation

        :param data: Upload data
        :raises serializers.ValidationError: If neither pdb code or pdb file were provided
        :raises serializers.ValidationError: If the protein file has the wrong filetype
        :raises serializers.ValidationError: If an invalid pdb code was provided
        :raises serializers.ValidationError: If an invalid uniprot code was provided
        :raises serializers.ValidationError: If the ligand file has the wrong filetype
        :return: Validated data
        """
        if data['pdb_code'] is None and data['protein_file'] is None:
            raise serializers.ValidationError('Neither pdb code not pdb file were provided.')
        if data['protein_file'] is not None:
            ext = os.path.splitext(data['protein_file'].name)[1]
            if ext != '.pdb':
                raise serializers.ValidationError(
                    'For proteins only pdb files are supported at the moment.'
                    )
        if data['pdb_code'] is not None:
            pdb_pattern = re.compile('[0-9][a-zA-Z0-9]{3}')
            if not pdb_pattern.match(data['pdb_code']):
                raise serializers.ValidationError(
                    'Invalid pdb code was provided.'
                    )
        if data['uniprot_code'] is not None:
            uniprot_pattern = re.compile(
                '[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}'
                )
            if not uniprot_pattern.match(data['uniprot_code']):
                raise serializers.ValidationError(
                    'Invalid uniprot code was provided.'
                    )
        if data['ligand_file'] is not None:
            ext = os.path.splitext(data['ligand_file'].name)[1]
            if ext != '.sdf':
                raise serializers.ValidationError(
                    'For ligands only sdf files are supported at the moment.'
                    )
        return data

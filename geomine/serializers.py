"""GeoMine model serializers"""
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSerializer, ProteinsPlusJobSubmitSerializer
from molecule_handler.input_validation import MoleculeInputValidator

from .models import GeoMineJob, GeoMineInfo


class GeoMineJobSerializer(ProteinsPlusJobSerializer):
    """Serializer for the GeoMineJob model"""

    class Meta:
        model = GeoMineJob
        fields = ProteinsPlusJobSerializer.Meta.fields + [
            'filter_file',
            'geomine_info'
        ]


class GeoMineInfoSerializer(serializers.ModelSerializer):
    """Serializer for the GeoMineInfo model"""

    class Meta:
        model = GeoMineInfo
        fields = ['id', 'info', 'parent_geomine_job']


class GeoMineJobSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """Serializer for the GeoMine job submission data"""

    filter_file = serializers.CharField(max_length=256)
    def validate(self, data):  # pylint: disable=arguments-renamed
        """Validate GeoMine submission data

        :param data: data to validate
        :type data: collections.OrderedDict
        :return: data
        :rtype: collections.OrderedDict
        """
        if 'filter_file' in data:
            if not data['filter_file'].endswith('.xml'):
                raise serializers.ValidationError(
                    'Filter file must end with .xml.')
        else:
            raise serializers.ValidationError(
                'Provide a filter file for querying the database.')
        return data

"""Base serializers for ProteinsPlus objects"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiResponse, OpenApiExample
from proteins_plus.job_handler import StatusField


class ProteinsPlusJobSerializer(serializers.ModelSerializer):
    """Base serializer for job models"""
    status = StatusField()

    class Meta:
        fields = ['id', 'status', 'date_created', 'date_last_accessed', 'error']


class ProteinsPlusJobSubmitSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Base serializer for job submit data"""
    use_cache = serializers.BooleanField(default=True)


class ProteinsPlusJobResponseSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Job submission response data"""
    job_id = serializers.UUIDField(required=True)
    retrieved_from_cache = serializers.BooleanField(default=False)

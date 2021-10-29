"""Base serializers for ProteinsPlus objects"""
from rest_framework import serializers

class ProteinsPlusJobSerializer(serializers.ModelSerializer):
    """Base serializer for job models"""
    class Meta:
        fields = ['id', 'status', 'date_created', 'date_last_accessed', 'error']

class ProteinsPlusJobSubmitSerializer(serializers.Serializer): # pylint: disable=abstract-method
    """Base serializer for job submit data"""
    use_cache = serializers.BooleanField(default=True)

class ProteinsPlusJobResponseSerializer(serializers.Serializer): # pylint: disable=abstract-method
    """Base serializer for response data after job submission"""
    job_id = serializers.UUIDField(required=True)
    retrieved_from_cache = serializers.BooleanField(default=False)

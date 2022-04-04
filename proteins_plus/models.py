"""Base models for ProteinsPlus objects"""
import uuid
from hashlib import blake2b
from django.db import models
from .job_handler import Status
from .utils import json_to_sorted_string


class ProteinsPlusBaseModel(models.Model):
    """Abstract base model for all objects"""

    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class ProteinsPlusHashableModel(ProteinsPlusBaseModel):
    """Abstract base model for hashable objects"""

    class Meta:
        abstract = True

    hash_attributes = []

    def generate_hashable_string(self):
        """Recursively generate string from attributes that can be used as input for a hash
        function

        :return: hashable string
        :rtype: str
        """
        hashable_substrings = []
        for attribute in self.hash_attributes:
            value = getattr(self, attribute)
            if isinstance(value, ProteinsPlusHashableModel):
                hashable_substrings.append(value.generate_hashable_string())
            elif isinstance(value, models.fields.files.FieldFile):
                hashable_substrings.append(value.read())
            elif isinstance(value, dict):
                # all hashable dicts are expected to be JSON-like objects.
                # A unique string representation of the intrinsically unordered
                # dict is generated.
                hashable_substrings.append(json_to_sorted_string(value, copy=True).encode('utf-8'))
            # add other unique field handlings here if str() is insufficient
            else:
                hashable_substrings.append(str(value).encode('utf-8'))
        hashable_string = b'_'.join(hashable_substrings)
        return hashable_string


class ProteinsPlusJob(ProteinsPlusHashableModel):
    """Abstract base model for job objects"""

    class Meta:
        abstract = True

    status = models.CharField(max_length=1, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(null=True)
    error_detailed = models.TextField(null=True)
    date_created = models.DateField(auto_now_add=True)
    date_last_accessed = models.DateField(auto_now=True)
    hash_value = models.CharField(max_length=256, null=True, default=None, unique=True)

    def set_hash_value(self):
        """Generate and set hash value for caching"""
        hasher = blake2b()
        hasher.update(self.generate_hashable_string())
        self.hash_value = hasher.hexdigest()

    def retrieve_job_from_cache(self):
        """If not present, generate and set hash value, then look for an equivalent object in cache

        :return: Cached job object or None
        :rtype: ProteinsPlusJob or None
        """
        if self.hash_value is None:
            self.set_hash_value()

        try:
            return self.__class__.objects.get(hash_value=self.hash_value)
        except self.__class__.DoesNotExist:
            return None

"""Helper functions for the molecule_handler unit tests"""
from proteins_plus.models import Status
from molecule_handler.test.utils import create_test_protein

from ..models import ProtossJob
from .config import TestConfig


def create_successful_protoss_job():
    """Helper function for creating dummy successful ProtossJob objects

    :return: Dummy ProtossJob object
    :rtype: ProtossJob
    """
    input_protein = create_test_protein(TestConfig.protein)
    output_protein = create_test_protein(TestConfig.protein)
    job = ProtossJob(
        input_protein=input_protein, output_protein=output_protein, status=Status.SUCCESS)
    job.save()
    return job

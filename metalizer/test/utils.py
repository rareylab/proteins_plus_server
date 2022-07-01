"""Helper functions for the Metalizer unit tests"""
from molecule_handler.test.utils import create_test_protein
from ..models import MetalizerJob, MetalizerInfo
from .config import TestConfig


def create_test_metalizer_job():
    """Helper function for creating dummy MetalizerJob objects

    :return: dummy MetalizerJob object
    :rtype: MetalizerJob
    """
    input_protein = create_test_protein(TestConfig.protein)
    job = MetalizerJob(
        input_protein=input_protein,
        residue_id='1300',
        chain_id='A',
        name='ZN',
        distance_threshold=2.8
    )
    job.save()
    return job


def create_successful_metalizer_job():
    """Helper function for creating dummy seccessful MetalizerJob objects

    :return: dummy MetalizerJob object
    :rtype: MetalizerJob
    """
    job = create_test_metalizer_job()
    output_protein = create_test_protein(TestConfig.protein)
    job.output_protein = output_protein
    with open(TestConfig.metalizer_result_file, encoding='utf8') as metalizer_result_file:
        job.metalizer_info = MetalizerInfo(
            parent_metalizer_job=job,
            info=metalizer_result_file.read()
        )
    job.metalizer_info.save()
    job.save()
    return job

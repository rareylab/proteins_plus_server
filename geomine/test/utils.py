"""Helper functions for the GeoMine unit tests"""
from molecule_handler.test.utils import create_test_protein
from ..models import GeoMineJob, GeoMineInfo
from .config import TestConfig


def create_test_geomine_job():
    """Helper function for creating dummy GeoMineJob objects

    :return: dummy GeoMineJob object
    :rtype: GeoMineJob
    """
    job = GeoMineJob(
        filter_file=TestConfig.filter_file
    )
    job.save()
    return job


def create_successful_geomine_job():
    """Helper function for creating dummy successful GeoMineJob objects

    :return: dummy GeoMineJob object
    :rtype: GeoMineJob
    """
    job = create_test_geomine_job()
    with open(TestConfig.geomine_result_file) as geomine_result_file:
        job.geomine_info = GeoMineInfo(parent_geomine_job=job, info=geomine_result_file.read())
    job.geomine_info.save()
    job.save()
    return job

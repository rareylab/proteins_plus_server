"""GeoMine celery tasks"""
from celery import shared_task
from proteins_plus.job_handler import execute_job

from .models import GeoMineJob
from .geomine_wrapper import GeoMineWrapper


@shared_task
def geomine_task(job_id):
    """GeoMine shared task

    :param job_id: id of the job to execute
    :type job_id: uuid
    """
    execute_job(geomine, job_id, GeoMineJob, 'GeoMine')


def geomine(job):
    """Execute GeoMine job

    :param job: GeoMine job to execute
    :type job: GeoMineJob
    """
    GeoMineWrapper.geomine(job)

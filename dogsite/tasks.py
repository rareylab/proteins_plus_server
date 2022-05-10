"""DoGSite celery tasks"""
from celery import shared_task
from proteins_plus.job_handler import execute_job

from .models import DoGSiteJob
from .dogsite_wrapper import DoGSiteWrapper


@shared_task
def dogsite_task(job_id):
    """DoGSite shared task

    :param job_id: id of the job to execute
    :type job_id: uuid
    """
    execute_job(dogsite, job_id, DoGSiteJob, 'DoGSite')


def dogsite(job):
    """Execute DoGSite job

    :param job: DoGSite job to execute
    :type job: DoGSiteJob
    """
    DoGSiteWrapper.dogsite(job)

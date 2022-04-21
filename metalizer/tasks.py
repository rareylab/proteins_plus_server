"""Metalizer celery tasks"""
from celery import shared_task
from proteins_plus.job_handler import execute_job

from .models import MetalizerJob
from .metalizer_wrapper import MetalizerWrapper


@shared_task
def metalize_task(job_id):
    """Metalizer shared task

    :param job_id: id of the job to execute
    :type job_id: uuid
    """
    execute_job(metalize, job_id, MetalizerJob, 'Metalizer')


def metalize(job):
    """Execute Metalizer job

    :param job: Metalizer job to execute
    :type job: MetalizerJob
    """
    MetalizerWrapper.metalize(job)

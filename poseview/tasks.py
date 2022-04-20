"""Poseview celery tasks"""
from celery import shared_task
from proteins_plus.job_handler import execute_job

from .models import PoseviewJob
from .poseview_wrapper import PoseviewWrapper


@shared_task
def poseview_task(job_id):
    """Poseview shared task

    :param job_id: id of the job to execute
    :type job_id: uuid
    """
    execute_job(poseview, job_id, PoseviewJob, 'Poseview')


def poseview(job):
    """Execute Poseview job

    :param job: Poseview job to execute
    :type job: PoseviewJob
    """
    PoseviewWrapper.poseview(job)

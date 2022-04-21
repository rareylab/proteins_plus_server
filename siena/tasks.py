"""siena celery tasks"""
from celery import shared_task
from proteins_plus.job_handler import execute_job
from .models import SienaJob
from .siena_wrapper import SienaWrapper


@shared_task
def siena_protein_task(job_id):
    """Start job execution

    :param job_id: Database id of the job object to be executed
    :type job_id: uuid
    """
    execute_job(siena_protein, job_id, SienaJob, 'Siena')


def siena_protein(job):
    """Run Siena job and store results into database

    :param job: SienaJob object containing the job data
    :type job: SienaJob
    """
    SienaWrapper.siena(job)

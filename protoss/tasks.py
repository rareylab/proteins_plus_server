"""protoss celery tasks"""
from celery import shared_task
from proteins_plus.job_handler import execute_job
from .models import ProtossJob
from .protoss_wrapper import ProtossWrapper

@shared_task
def protoss_protein_task(job_id):
    """Start job execution

    :param job_id: Database id of the job object to be executed
    :type job_id: int
    """
    execute_job(protoss_protein, job_id, ProtossJob, 'Protoss')

def protoss_protein(job):
    """Protoss Protein object and store a new Protein object into the database

    :param job: ProtossJob object containing the job data
    :type job: ProtossJob
    """
    ProtossWrapper.protoss(job)

"""ediascorer celery tasks"""
from celery import shared_task

from proteins_plus.job_handler import execute_job
from .models import EdiaJob
from .ediascorer_wrapper import EdiascorerWrapper


@shared_task
def ediascore_protein_task(job_id):
    """Start job execution

    :param job_id: Database id of the job object to be executed
    :type job_id: int
    """
    execute_job(ediascore_protein, job_id, EdiaJob, 'EDIAscorer')



def ediascore_protein(job):
    """Execute the Ediascorer on a Protein object and store the results into new database objects

    :param job: EdiaJob object containing the job data
    :type job: EdiaJob
    """
    EdiascorerWrapper.ediascore(job)

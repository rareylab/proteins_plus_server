"""molecule_handler celery tasks"""
from celery import shared_task
from proteins_plus.job_handler import execute_job
from .preprocessor_wrapper import PreprocessorWrapper
from .models import PreprocessorJob


@shared_task
def preprocess_molecule_task(job_id):
    """Start job execution

    :param job_id: Database id of the job object to be executed
    :type job_id: int
    """
    execute_job(preprocess_molecule, job_id, PreprocessorJob, 'Preprocessor')


def preprocess_molecule(job):
    """Preprocess Protein and Ligand information and store it into the database

    :param job: PreprocessorJob object containing the job data
    :type job: PreprocessorJob
    """
    PreprocessorWrapper.preprocess(job)

"""Structureprofiler celery tasks"""
from celery import shared_task
from proteins_plus.job_handler import execute_job
from molecule_handler.models import ElectronDensityMap
from .models import StructureProfilerJob
from .structureprofiler_wrapper import StructureProfilerWrapper


@shared_task
def structureprofiler_protein_task(job_id):
    """Start job execution
    :param job_id: Database id of the job object to be executed
    :type job_id: int
    """
    execute_job(structureprofiler_protein, job_id, StructureProfilerJob, 'StructureProfiler')


def structureprofiler_protein(job):
    """ Execute the Structureprofiler on a Protein object
    and store the results into new database objects

    :param job: Structurprofiler object containing the job data
    :type job: StructureProfilerjob
    """
    if job.electron_density_map is None and job.density_file_pdb_code:
        job.electron_density_map = ElectronDensityMap.from_pdb_code(job.density_file_pdb_code)
        if not job.electron_density_map:
            raise RuntimeError(
                f"Error while retrieving density file with pdb code {job.density_file_pdb_code}\n"
            )
        job.save()
    StructureProfilerWrapper.structureprofiler(job)

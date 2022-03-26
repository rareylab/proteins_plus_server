"""ediascorer celery tasks"""
from tempfile import TemporaryFile
import requests
from celery import shared_task
from django.conf import settings
from django.core.files import File
from proteins_plus.job_handler import execute_job
from molecule_handler.models import ElectronDensityMap
from .models import EdiaJob
from .ediascorer_wrapper import EdiascorerWrapper


@shared_task
def ediascore_protein_task(job_id):
    """Start job execution

    :param job_id: Database id of the job object to be executed
    :type job_id: int
    """
    execute_job(ediascore_protein, job_id, EdiaJob, 'EDIAscorer')


def get_density_file(job):
    """Fetch electron density file from server and save it as a new ElectronDensityMap instance

    :param job: Job object that the ElectronDensityMap object will be assiciated with
    :type job: EdiaJob
    :raises Exception: If an error occurs while downloading the electron density file
    """
    density_map = ElectronDensityMap()
    pdb_code = job.density_file_pdb_code

    url = f'{settings.URLS["density_files"]}{pdb_code}.ccp4'
    req = requests.get(url)
    if req.status_code != 200:
        raise RuntimeError(
            f"Error while retrieving density file with pdb code {pdb_code}\n" +
            f"Request: GET {url}\n" +
            f"Response: \n{req.text}"
        )

    with TemporaryFile() as tmpfile:
        content_as_bytes = bytearray(req.content)
        tmpfile.write(content_as_bytes)
        tmpfile.seek(0)
        density_map.file.save(f'{pdb_code}.ccp4', File(tmpfile))
        density_map.save()

    job.electron_density_map = density_map
    job.save()


def ediascore_protein(job):
    """Execute the Ediascorer on a Protein object and store the results into new database objects

    :param job: EdiaJob object containing the job data
    :type job: EdiaJob
    """
    if job.electron_density_map is None:
        get_density_file(job)
    EdiascorerWrapper.ediascore(job)

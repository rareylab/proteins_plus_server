"""Common classes and functions for all apps"""
import logging
import traceback

logger = logging.getLogger(__name__)

class Status:  # pylint: disable=too-few-public-methods
    """Class wrapping a status enum"""
    PENDING = 'p'
    RUNNING = 'r'
    SUCCESS = 's'
    FAILURE = 'f'

    DETAILED = {PENDING: 'pending', RUNNING: 'running', SUCCESS: 'success', FAILURE: 'failure'}

    choices = [
        (PENDING, DETAILED[PENDING]),
        (RUNNING, DETAILED[RUNNING]),
        (SUCCESS, DETAILED[SUCCESS]),
        (FAILURE, DETAILED[FAILURE]),
    ]

    @staticmethod
    def to_string(status):
        """Convert status to a readable string

        :param status: status abbreviation
        :type status: str
        :return: detailed status name
        :rtype: str
        """
        return Status.DETAILED[status]

def execute_job(task, job_id, job_type, tool_name):
    """Execute Job as a celery task following a centralized workflow

    :param task: task to be executed
    :type task: function
    :param job_id: Id of the job object
    :type job_id: int
    :param job_type: Database table in which to find the job object
    :type job_type: django.db.models.Model
    :raises error: If an error occurs during job execution
    """

    logger.info(f'Started task. Executing {task} on {job_type} with id {job_id}.')
    job = job_type.objects.get(id=job_id)
    try:
        job.status = Status.RUNNING
        job.save()

        task(job)
    except Exception as error:
        job.status = Status.FAILURE
        job.hash_value = None
        job.error = f'An error occurred during the execution of {tool_name}.'
        job.error_detailed = traceback.format_exc()
        job.save()

        logger.error(
            f'Error occured during execution of task {task} on {job_type} with id {job_id}.\n' +
            f'Error: \n\t{traceback.format_exc()}'
        )
        raise error
    else:
        job.status = Status.SUCCESS
        job.save()
        logger.info(f'Successfully finished executing {task} on {job_type} with id {job_id}.')

def submit_task(job, task, use_cache):
    """Retrieve an existing job from cache or start its execution

    :param job: Job to be executed or retrieved from cache
    :type job: ProteinsPlusJob
    :param task: The task function to be called if no caching occurrs
    :type task: celery.local.celery.local (celery shared task)
    :param use_cache: Indicates whether caching should be used
    :type use_cache: bool
    :return: A dictionary containing the response information for the user
    :rtype: dict('job_id': UUID, 'retrieved_from_cache': bool)
    """
    cached_job = None
    retrieved_from_cache = False
    if use_cache and len(job.hash_attributes) != 0:
        cached_job = job.retrieve_job_from_cache()
    if cached_job is None:
        job.save()
        task.delay(job.id)
    else:
        job = cached_job
        retrieved_from_cache = True

    response_data = {'job_id': job.id, 'retrieved_from_cache': retrieved_from_cache}
    return response_data

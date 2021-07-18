"""Utility functions for all apps"""
import logging
import traceback
from rest_framework import serializers
from django.db import models

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

class ProteinsPlusJob(models.Model):
    """Abstract model for Job objects"""
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(null=True)
    error_detailed = models.TextField(null=True)
    date_created = models.DateField(auto_now_add=True)
    date_last_accessed = models.DateField(auto_now=True)

    class Meta:
        abstract=True

class ProteinsPlusJobSerializer(serializers.ModelSerializer):
    """Abstract model for job serializer"""
    class Meta:
        fields = ['id', 'status', 'date_created', 'date_last_accessed', 'error']

class JobSubmitResponseSerializer(serializers.Serializer): # pylint: disable=abstract-method
    """Serializer for response data of job submission requests"""
    job_id = serializers.IntegerField(required=True)

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

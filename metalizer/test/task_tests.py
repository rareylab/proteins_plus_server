"""Metalizer task tests"""
import json

from proteins_plus.test.utils import PPlusTestCase
from proteins_plus.models import Status

from ..models import MetalizerJob
from ..tasks import metalize_task
from .config import TestConfig
from .utils import create_test_metalizer_job


class TaskTests(PPlusTestCase):
    """Metalizer task tests"""

    def test_metalize(self):
        """Test Metalizer execution produces expected results"""
        job = create_test_metalizer_job()
        metalize_task.run(job.id)
        job = MetalizerJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertIsNotNone(job.metalizer_info)
        with open(TestConfig.metalizer_result_file) as metalizer_result_file:
            metalizer_result = json.load(metalizer_result_file)
        self.assertEqual(job.metalizer_info.info, metalizer_result)

"""Metalizer task tests"""
import json

from proteins_plus.test.utils import PPlusTestCase
from proteins_plus.models import Status
from molecule_handler.test.utils import create_test_protein

from .config import TestConfig
from ..models import MetalizerJob
from ..tasks import metalize_task


class TaskTests(PPlusTestCase):
    """Metalizer task tests"""

    def test_metalize(self):
        """Test Metalizer execution produces expected results"""
        input_protein = create_test_protein(TestConfig.protein)

        job = MetalizerJob(
            input_protein=input_protein,
            residue_id=1300,
            chain_id='A',
            name='ZN',
            distance_threshold=2.8
        )
        job.save()

        metalize_task.run(job.id)
        job = MetalizerJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.output_protein)
        self.assertIsNotNone(job.metalizer_result)
        with open(TestConfig.metalizer_result_file) as metalizer_result_file:
            metalizer_result = json.load(metalizer_result_file)
        self.assertEqual(job.metalizer_result, metalizer_result)

"""GeoMine task tests"""
import json
import os
import unittest

from proteins_plus.test.utils import PPlusTestCase, is_tool_available
from proteins_plus.models import Status

from ..models import GeoMineJob
from ..settings import GeoMineSettings
from ..tasks import geomine_task
from .utils import create_test_geomine_job


class TaskTests(PPlusTestCase):
    """GeoMine task tests"""

    def test_available(self):
        """Test if binary exists at the correct location and is licensed"""
        self.assertEqual(is_tool_available('geomine'), 64,
                         'Ran with unexpected error code. Is it licensed?')

    @unittest.skipIf(GeoMineSettings.GEOMINE_HOSTNAME == '',
                     "GeoMine postgres hostname environment variable \
                      not set.")
    def test_geomine(self):
        """Test GeoMine execution produces expected results"""
        job = create_test_geomine_job()
        geomine_task.run(job.id)
        job = GeoMineJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertIsNotNone(job.geomine_info)

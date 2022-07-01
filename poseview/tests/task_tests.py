"""Poseview task tests"""
import os
import subprocess

from proteins_plus.models import Status
from proteins_plus.test.utils import PPlusTestCase
from proteins_plus import settings

from ..tasks import poseview_task
from ..models import PoseviewJob
from .utils import create_poseview_job


class TaskTests(PPlusTestCase):
    """Poseview task tests"""

    def test_available(self):
        """Test if binary exists at the correct location and is licensed"""
        # poseview must be called in the directory it is in because of licensing
        poseview_basename = os.path.basename(settings.BINARIES['poseview'])
        poseview_directory = os.path.dirname(settings.BINARIES['poseview'])
        args = ['./' + poseview_basename, '-h']
        process = subprocess.run(args, stdout=subprocess.DEVNULL, cwd=poseview_directory)  # pylint: disable=subprocess-run-check
        self.assertEqual(process.returncode, 0)

    def test_poseview(self):
        """Test Poseview execution produces expected results"""
        job = create_poseview_job()
        poseview_task.run(job.id)
        job = PoseviewJob.objects.get(id=job.id)
        self.assertEqual(job.status, Status.SUCCESS)
        self.assertTrue(job.image.name)

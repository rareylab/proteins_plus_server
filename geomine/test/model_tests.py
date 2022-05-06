"""GeoMine model tests"""
from proteins_plus.test.utils import PPlusTestCase

from ..models import GeoMineInfo, GeoMineJob
from .utils import create_test_geomine_job, create_successful_geomine_job


class ModelTests(PPlusTestCase):
    """GeoMine model tests"""

    def test_cache_behavior(self):
        """Test caching behavior of GeoMine jobs"""
        job = create_test_geomine_job()
        job.set_hash_value()
        job.save()

        other_job = create_test_geomine_job()
        cached_job = other_job.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        another_job = create_test_geomine_job()
        another_job.filter_file = "otherFilter.xml"
        another_job.save()
        cached_job = another_job.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

    def test_job_delete_cascade(self):
        """Test cascading deletion behavior"""
        job = create_successful_geomine_job()
        geomine_info = job.geomine_info
        job.delete()
        # deleting the job deletes the GeoMine info but not the protein
        self.assertFalse(GeoMineInfo.objects.filter(id=geomine_info.id).exists())

        # test delete DoGSiteInfo
        job = create_successful_geomine_job()
        geomine_info = job.geomine_info
        geomine_info.delete()
        # deleting the GeoMine info deletes the job but not the protein
        self.assertFalse(GeoMineJob.objects.filter(id=job.id).exists())

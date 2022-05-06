"""Django friendly wrapper of the GeoMine"""
import os
import json
import logging
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from proteins_plus import settings

from .models import GeoMineInfo
from .settings import GeoMineSettings

logger = logging.getLogger(__name__)


class GeoMineWrapper:
    """Django friendly wrapper of the GeoMine"""

    @staticmethod
    def geomine(job):
        """Execute GeoMine and load the results

        :param job: GeoMine job
        :type job: GeoMineJob
        """
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)
            geomine_result_path = GeoMineWrapper.execute_geomine(job, dir_path)
            GeoMineWrapper.load_results(job, geomine_result_path)

    @staticmethod
    def execute_geomine(job, dir_path):
        """Execute GeoMine

        :param job: GeoMine job
        :type job: GeoMineJob
        :param dir_path: directory to execute GeoMine in
        :type dir_path: Path
        :return: path to output protein and path to GeoMine info
        :rtype: (Path, Path)
        """
        geomine_result_path = dir_path / 'geomine_result.json'

        args = [
            settings.BINARIES['geomine'],
            '--database', GeoMineSettings.GEOMINE_DB_NAME,
            '--dbIsPostgres',
            '--hostname', GeoMineSettings.GEOMINE_HOSTNAME,
            '--username', GeoMineSettings.GEOMINE_PGUSER_ENV_VAR,
            '--password', GeoMineSettings.GEOMINE_PGPASSWORD_ENV_VAR,
            '--webserverSearch',
            '--query', f'{job.filter_file}',
            '--webserverOutput', str(geomine_result_path)
        ]
        logger.info('Executing command line call: %s', " ".join(args))
        subprocess.check_call(args)
        return geomine_result_path

    @staticmethod
    def load_results(job, geomine_result_path):
        """Load GeoMine results into the database

        :param job: GeoMine job
        :type job: GeoMineJob
        :param geomine_result_path: path to the GeoMine JSON output
        :type geomine_result_path: Path
        """
        with open(geomine_result_path) as geomine_result_file:
            geomine_data = json.load(geomine_result_file)
        if not len(geomine_data) > 0:
            raise RuntimeError('GeoMine did not generate results')
        geomine_info = GeoMineInfo(info=geomine_data, parent_geomine_job=job)
        geomine_info.save()
        job.geomine_info = geomine_info
        job.save()

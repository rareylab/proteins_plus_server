"""Django friendly wrapper of the DoGSite"""
import logging
import csv
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from django.core.files import File
from proteins_plus import settings
from molecule_handler.models import ElectronDensityMap, ProteinSite

from .models import DoGSiteInfo

logger = logging.getLogger(__name__)


class DoGSiteWrapper:
    """Django friendly wrapper of the DoGSite"""

    @staticmethod
    def dogsite(job):
        """Execute DoGSite and load the results

        :param job: DoGSite job
        :type job: DoGSiteJob
        """
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)
            DoGSiteWrapper.execute_dogsite(job, dir_path)
            DoGSiteWrapper.load_results(job, dir_path)

    @staticmethod
    def execute_dogsite(job, dir_path):
        """Execute DoGSite

        :param job: DoGSite job
        :type job: DoGSiteJob
        :param dir_path: directory to execute DoGSite in
        :type dir_path: Path
        """
        # files are created in dir_path and named with the prefix 'output'
        output_file_name_prefix = 'output'
        dogsite_result_path = dir_path / output_file_name_prefix
        with job.input_protein.write_temp() as protein_file:
            args = [
                settings.BINARIES['dogsite'],
                '--proteinFile', protein_file.name,
                '--outputName', str(dogsite_result_path),
                '--writeSiteResiduesEDF',
                '--writeGridAllCCP4',
                '--writeDescToFile'
            ]

            if job.input_ligand:
                tmp_file = job.input_ligand.write_temp()
                args.append('--ligandFile')
                args.append(tmp_file.name)
            if job.chain_id:
                args.append('--chain')
                args.append(str(job.chain_id))
            if job.calc_subpockets:
                args.append('--subpocDetect')
            if job.ligand_bias:
                args.append('--useLigandsToAnnotateGrid')

            logger.debug('Executing command line call: %s', " ".join(args))
            subprocess.check_call(args, stdout=subprocess.DEVNULL)

    @staticmethod
    def load_results(job, dir_path):
        """Load DoGSite results into the database

        :param job: DoGSite job
        :type job: DoGSiteJob
        :param dir_path: path to the DoGSite output
        :type dir_path: Path
        """
        statistic_dict = DoGSiteWrapper.load_result_statistic(dir_path)
        nof_dogsite_hits = len(statistic_dict)
        if nof_dogsite_hits == 0:
            # no results found by DoGSite
            job.save()
            return
        dogsite_info = DoGSiteInfo(info=statistic_dict, parent_dogsite_job=job)
        dogsite_info.save()
        job.dogsite_info = dogsite_info

        edf_files = DoGSiteWrapper.load_result_pockets(dir_path, nof_dogsite_hits)
        # Put DoGSite results into ProteinSite models.
        for edf_file_path in edf_files:
            proteinsite = ProteinSite.from_edf(job.input_protein, Path(edf_file_path))
            proteinsite.save()
            job.output_pockets.add(proteinsite)

        density_files = DoGSiteWrapper.load_result_pocket_densities(dir_path, nof_dogsite_hits)
        for density_file_path in density_files:
            density_map = ElectronDensityMap.from_ccp4(density_file_path)
            density_map.save()
            job.output_densities.add(density_map)

        job.save()

    @staticmethod
    def load_result_pockets(pocket_dir, nof_results):
        """Loads detected pockets of DoGSite algorithm.

        All detected pockets are gathered from disc and returned.

        :param pocket_dir: Path to dogsite result directory
        :type pocket_dir: pathlib.Path
        :param nof_results: number of DoGSite pockets to expect
        :type nof_results: int
        """
        edf_files = list(pocket_dir.glob('*.edf'))

        if len(edf_files) != nof_results:
            raise RuntimeError('DoGSite: Error inconsistency between result EDF files and '
                               'statistics report')

        return edf_files

    @staticmethod
    def load_result_pocket_densities(density_dir, nof_results):
        """Loads densities of detected pockets.

        All detected pockets are gathered from disc and returned.

        :param density_dir: Path to dogsite result directory
        :type density_dir: pathlib.Path
        :param nof_results: number of DoGSite pockets to expect
        :type nof_results: int
        """
        density_files = list(density_dir.glob('*.ccp4'))

        if len(density_files) != nof_results:
            raise RuntimeError('DoGSite: Error inconsistency between result CCP4 files and '
                               'statistics report')

        return density_files

    @staticmethod
    def load_result_statistic(path):
        """Loads result statistic TXT.

        :param path: path to result directory
        :type path: pathlib.Path
        :return: A dict containing the CSV data
        :rtype: dict
        """
        txt_file = path / 'output_desc.txt'
        if not txt_file.is_file():
            raise RuntimeError('DoGSite: Internal error, no output descriptor file found.')
        data = []
        with open(txt_file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter='\t')
            for row in csv_reader:
                data_dict = {}
                for k, val in row.items():
                    if k is not None:
                        data_dict[k] = val
                data.append(data_dict)
        return data

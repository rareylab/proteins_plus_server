"""A django model friendly wrapper around SIENA binary"""
import logging
import csv
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from molecule_handler.models import Protein, Ligand
from siena.models import SienaInfo
from siena.settings import SienaSettings

logger = logging.getLogger(__name__)


class SienaWrapper:
    """A django model friendly wrapper around the SIENA binary"""

    @staticmethod
    def siena(job):
        """Run SIENA for a Protein object from the database.
            Create new Object instances for the results.

        :param job: Contains the input Protein and binding site specification for the SIENA run
        :type job: SienaJob
        """
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)
            SienaWrapper.execute_siena(job, dir_path)
            SienaWrapper.load_results(job, dir_path)

    @staticmethod
    def execute_siena(job, directory):
        """Execute SIENA on a given Protein and binding site object

        :param job: Contains the input Protein and binding site specification for the SIENA run
        :type job: SienaJob
        :param directory: Path to desired output directory
        :type directory: Path
        :param siena_search_db_path: Path to siena site search database
        :type siena_search_db_path: Path or None
        :raises CalledProcessError: If an error occurs during SIENA execution
        """
        protein = job.input_protein
        ligand = job.input_ligand
        site = job.input_site

        with protein.write_temp() as protein_file:

            args = [
                settings.BINARIES['siena'],
                '--protein', protein_file.name,
                '--database', str(Path(SienaSettings.SIENA_SEARCH_DB).resolve()),
                '--output', str(directory.resolve())
            ]

            tmp_file = None
            if ligand:
                tmp_file = ligand.write_temp()
                args.append('--ligand')
            elif site:
                tmp_file = site.write_edf_temp(protein_file.name)
                args.append('--edf')
            else:
                raise ValueError('No valid input binding site specification')
            args.append(tmp_file.name)

            logger.info('Executing command line call: %s', " ".join(args))
            subprocess.check_call(args)

    @staticmethod
    def load_results(job, path):
        """Store all SIENA results in the database

        :param job: Job object where the resulting output objects will be stored
        :type job: SienaJob
        :param path: Path to the output directory
        :type path: Path
        """
        statistic_dict = SienaWrapper.load_result_statistic(path)
        nof_siena_hits = len(statistic_dict)
        if nof_siena_hits == 0:
            # no results found by SIENA
            job.save()
            return
        output_info = SienaInfo(parent_siena_job=job, statistic=statistic_dict,
                                alignment=SienaWrapper.load_result_alignment(path))
        output_info.save()
        job.output_info = output_info
        pdb_files, sdf_files_dict = SienaWrapper.load_result_proteins_and_ligands(path,
                                                                                  nof_siena_hits)
        # Put Siena results into Protein and Ligand models.
        # Ligand models are associated with their respective Protein model.
        for pdb_file_path in pdb_files:
            with pdb_file_path.open('r') as pdb_file:
                pdb_string = pdb_file.read()
            file_basename = pdb_file_path.name.split('.')[0]
            protein = Protein(name=file_basename,
                              file_type='pdb',
                              file_string=pdb_string)
            protein.save()
            if file_basename in sdf_files_dict:
                ligand_file_path = sdf_files_dict[file_basename]
                with open(ligand_file_path, 'r', encoding='utf8') as ligand_file:
                    ligand = Ligand(protein=protein,
                                    name=file_basename,
                                    file_type='sdf',
                                    file_string=ligand_file.read())
                ligand.save()
            job.output_proteins.add(protein)

        job.save()

    @staticmethod
    def load_result_proteins_and_ligands(path, nof_results):
        """Loads protein and ligand hits of Siena search.

        All protein and ligand hits are gathered from disc and returned.

        :param path: Path to siena result directory
        :type path: pathlib.Path
        :param nof_results: number of SIENA hits to expect
        :type nof_results: int
        """
        ensemble_dir = path / 'ensemble'
        if not ensemble_dir.is_dir():
            raise RuntimeError('Siena: Error no result ensemble directory')
        pdb_files = list(ensemble_dir.glob('*.pdb'))

        if len(pdb_files) != nof_results:
            raise RuntimeError('Siena: Error inconsistency between result PDB files and CSV report')

        ligand_dir = path / 'ligands'
        if not ligand_dir.is_dir():
            raise RuntimeError('Siena: Error no result ligand directory')
        sdf_files_dict = {file.name.split('.')[0]: file for file in ligand_dir.glob('*.sdf')}

        return pdb_files, sdf_files_dict

    @staticmethod
    def load_result_alignment(path):
        """Loads alignment file as string

        :param path: path to alignment file
        :type path: pathlib.Path
        :return: Alignment file content as string
        :rtype: str
        """
        alignment_file = path / 'alignment.txt'
        if not alignment_file.is_file():
            raise RuntimeError('Siena: Error loading alignment.txt file')
        with open(alignment_file, 'r', encoding='utf8') as file:
            return file.read()

    @staticmethod
    def load_result_statistic(path):
        """Loads result statistic CSV.

        :param path: path to result directory
        :type path: pathlib.Path
        :return: A dict containing the CSV data
        :rtype: dict
        """
        csv_file = path / 'resultStatistic.csv'
        if not csv_file.is_file():
            return {}  # SIENA did not find any results
        data = []
        with open(csv_file, 'r', encoding='utf8') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            for row in csv_reader:
                data_dict = {}
                for k, val in row.items():
                    if len(k) > 0:
                        val_stripped = val.strip()
                        if len(val_stripped) > 0:
                            data_dict[k] = val_stripped
                        else:
                            data_dict[k] = None
                data.append(data_dict)
        return data

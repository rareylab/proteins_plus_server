"""Django friendly wrapper of the Metalizer"""
import json
import logging
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from proteins_plus import settings
from molecule_handler.models import Protein

from .models import MetalizerInfo

logger = logging.getLogger(__name__)


class MetalizerWrapper:
    """Django friendly wrapper of the Metalizer"""

    @staticmethod
    def metalize(job):
        """Execute Metalizer and load the results

        :param job: Metalizer job
        :type job: MetalizerJob
        """
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)
            metalized_protein_path, metalizer_result_path = \
                MetalizerWrapper.execute_metalizer(job, dir_path)
            MetalizerWrapper.load_results(job, metalized_protein_path, metalizer_result_path)

    @staticmethod
    def execute_metalizer(job, dir_path):
        """Execute Metalizer

        :param job: Metalizer job
        :type job: MetalizerJob
        :param dir_path: directory to execute Metalizer in
        :type dir_path: Path
        :return: path to output protein and path to Metalizer info
        :rtype: (Path, Path)
        """
        metalized_protein_path = dir_path / 'metalized.pdb'
        metalizer_result_path = dir_path / 'metalizer_result.json'
        with job.input_protein.write_temp() as protein_file:
            with open(metalizer_result_path, 'w') as metalizer_result_file:
                args = [
                    settings.BINARIES['metalizer'],
                    '--input', protein_file.name,
                    '--metal', f'{job.residue_id}:{job.chain_id}.{job.name}',
                    '--distance_threshold', str(job.distance_threshold),
                    '--crystal_symmetry',
                    '--angle_threshold', str(21.5),
                    '--max_free_sites', str(0.25),
                    '--output', str(metalized_protein_path)
                ]
                logger.info('Executing command line call: %s', " ".join(args))
                subprocess.check_call(args, stdout=metalizer_result_file)
        return metalized_protein_path, metalizer_result_path

    @staticmethod
    def load_results(job, metalized_protein_path, metalizer_result_path):
        """Load Metalizer results into the database

        :param job: Metalizer job
        :type job: MetalizerJob
        :param metalized_protein_path: path to the Metalizer output protein
        :type metalized_protein_path: Path
        :param metalizer_result_path: path to the Metalizer JSON output
        :type metalizer_result_path: Path
        """
        with open(metalizer_result_path) as metalizer_result_file:
            metalizer_data = json.load(metalizer_result_file)
        if not len(metalizer_data) > 0:
            raise RuntimeError('Metalizer did not generate results')
        metalizer_info = MetalizerInfo(info=metalizer_data[0], parent_metalizer_job=job)
        metalizer_info.save()
        job.metalizer_info = metalizer_info
        with open(metalized_protein_path) as metalizer_protein_file:
            pdb_string = metalizer_protein_file.read()
        output_protein = Protein(
            name=job.input_protein.name,
            pdb_code=job.input_protein.pdb_code,
            uniprot_code=job.input_protein.uniprot_code,
            file_type='pdb',
            file_string=pdb_string
        )
        output_protein.save()
        job.output_protein = output_protein
        job.save()

"""A django model friendly wrapper around the protoss binary"""
import os
import logging
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from django.conf import settings

from molecule_handler.models import Protein
from molecule_handler.utils import load_processed_ligands

logger = logging.getLogger(__name__)


class ProtossWrapper:
    """A django model friendly wrapper around the protoss binary"""

    @staticmethod
    def protoss(job):
        """Protoss Protein objects. Create new object instances for the protossed files.

        :param job: Contains the Protein objects that should be protossed
        :type job: ProtossJob
        """
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)
            ProtossWrapper.execute_protoss(job, dir_path)
            ProtossWrapper.load_results(job, dir_path)

    @staticmethod
    def execute_protoss(job, directory):
        """Execute the protoss binary on the Protein object specified in
        the job.

        :param job: Contains the Protein object that should be protossed
        :type job: ProtossJob
        :param directory: Path to desired output directory
        :type directory: Path
        """
        protein_file = job.input_protein.write_temp()
        if job.input_ligand:
            # use custom ligand if one was given
            ligand_file = job.input_ligand.write_temp()
        else:
            # use associated ligands if not custom ligand was given
            ligand_file = job.input_protein.write_ligands_temp()

        args = [
            settings.BINARIES['protoss'],
            '--input', protein_file.name,
            '--output', os.path.join(str(directory.absolute()), 'protein_out.pdb')
        ]
        if ligand_file:
            args.extend(['--ligand_input', ligand_file.name,
                         '--ligand_output',
                         os.path.join(str(directory.absolute()), 'ligand_out.sdf')])

        logger.debug('Executing command line call: %s', " ".join(args))
        subprocess.check_call(args)

    @staticmethod
    def load_results(job, path):
        """Store the results as new objects in the database

        :param job: Job object where the resulting output objects will be stored
        :type job: ProtossJob
        :param path: Path to the output directory
        :type path: Path
        """
        ProtossWrapper.load_protossed_protein(job, path)
        load_processed_ligands(path, job.output_protein)
        job.save()

    @staticmethod
    def load_protossed_protein(job, path):
        """Store the pdb file string that was generated by protoss in a new Protein database object

        :param job: Job object where the resulting output protein will be stored
        :type job: ProtossJob
        :param path: Path to the output directory
        :type path: Path
        :raises RuntimeError: If no pdb file was generated by the preprocessor
        """
        pdb_files = list(path.glob('*.pdb'))
        if len(pdb_files) != 1:
            raise RuntimeError('Protoss: Error loading output file')
        with pdb_files[0].open() as pdb_file:
            pdb_string = pdb_file.read()

        job.output_protein = Protein(
            name=job.input_protein.name,
            pdb_code=job.input_protein.pdb_code,
            uniprot_code=job.input_protein.uniprot_code,
            file_type='pdb',
            file_string=pdb_string
        )
        job.output_protein.save()

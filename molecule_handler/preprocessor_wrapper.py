"""A django model friendly wrapper around the preprocessor binary"""
import logging
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile
from contextlib import nullcontext

from django.conf import settings
from django.core.files import File

from .models import Protein, Ligand

logger = logging.getLogger(__name__)


class PreprocessorWrapper:
    """A django model friendly wrapper around the preprocessor binary"""

    @staticmethod
    def preprocess(job):
        """Preprocess molecule strings. Create new Protein and Ligand instances
        with preprocessed file strings.

        :param job: Contains the molecule strings that should be preprocessed
        :type job: PreprocessorJob
        """
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)
            PreprocessorWrapper.execute_preprocessing(job, dir_path)
            PreprocessorWrapper.load_results(job, dir_path)

    @staticmethod
    def execute_preprocessing(job, directory):
        """Execute the preprocessor binary on the molecule strings specified in
        the job. If a ligand was explicitly specified it is considered in the commandline call.

        :param job: Contains the molecule strings that should be preprocessed
        :type job: PreprocessorJob
        :param directory: Path to desired output directory
        :type directory: Path
        """
        with PreprocessorWrapper.create_temp_molecule_file(job.protein_string, 'pdb') \
                as protein_file, \
                PreprocessorWrapper.create_temp_molecule_file(job.ligand_string, 'sdf') \
                        as ligand_file:
            args = [
                settings.BINARIES['preprocessor'],
                '--protein', protein_file.name,
                '--outdir', str(directory.absolute()),
            ]
            if ligand_file:
                args.extend(['--ligand', ligand_file.name])

            logger.debug('Executing command line call: %s', " ".join(args))
            subprocess.check_call(args)

    @staticmethod
    def create_temp_molecule_file(filestring, file_type):
        """Write a given molecule strings to a temporary file

        :param filestring: The molecule string that should be written
        :type filestring: str
        :return: A temporary file or None, if the input string was None
        :rtype: NamedTemporaryFile or None
        """
        if filestring is None:
            return nullcontext(None)

        tmpfile = NamedTemporaryFile('w+', suffix=f'.{file_type}')
        tmpfile.write(filestring)
        tmpfile.seek(0)

        return tmpfile

    @staticmethod
    def load_results(job, path):
        """Store the results as new objects in the database

        :param job: Job object where the resulting output objects will be stored
        :type job: PreprocessorJob
        :param path: Path to the output directory
        :type path: Path
        """
        PreprocessorWrapper.load_protein(job, path)
        PreprocessorWrapper.load_ligands(path, job.output_protein)
        job.save()

    @staticmethod
    def load_protein(job, path):
        """Store the generated pdb file string in a new Protein database object

        :param job: Job object where the resulting output protein will be stored
        :type job: PreprocessorJob
        :param path: Path to the output directory
        :type path: Path
        :raises RuntimeError: If no pdb file was generated by the preprocessor
        """
        pdb_files = list(path.glob('*.pdb'))
        if len(pdb_files) != 1:
            raise RuntimeError('Preprocessor: Error loading output file')
        with pdb_files[0].open() as pdb_file:
            pdb_string = pdb_file.read()
        job.output_protein = Protein(
            name=job.protein_name,
            pdb_code=job.pdb_code,
            uniprot_code=job.uniprot_code,
            file_type='pdb',
            file_string=pdb_string
        )
        job.output_protein.save()

    @staticmethod
    def load_ligands(path, protein):
        """Store the generated sdf file string in a new Ligand database object

        :param path: Path to the output directory
        :type path: Path
        :param protein: Protein object that the Ligand objects should be associated with
        :type protein: Protein
        """
        sd_files = list(path.glob('*.sdf'))
        image_files = list(path.glob('*.svg'))

        for sd_file in sd_files:
            ligand_name = sd_file.stem
            with sd_file.open() as ligand_file:
                ligand = Ligand.from_file(ligand_file, protein)
            image_name = f'{ligand_name}.svg'
            for image in image_files:
                if image.name == image_name:
                    new_image_name = f'{ligand_name}_{ligand.id}.svg'
                    ligand.image.save(new_image_name, File(image.open('rb')))
                break
            ligand.save()

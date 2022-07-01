"""A django model friendly wrapper around the edia scorer binary"""
import logging
import csv
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from molecule_handler.utils import load_processed_ligands
from molecule_handler.models import Protein
from ediascorer.models import EdiaScores

logger = logging.getLogger(__name__)


class EdiascorerWrapper:
    """A django model friendly wrapper around the Ediascorer binary"""

    @staticmethod
    def ediascore(job):
        """Run the Ediascorer for a Protein object from the database.
            Create new Object instances for the results.

        :param job: Contains the input Protein and ElectronDensityMap for the Ediascorer run
        :type job: EdiaJob
        """
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)
            EdiascorerWrapper.execute_ediascorer(job, dir_path)
            EdiascorerWrapper.load_results(job, dir_path)

    @staticmethod
    def execute_ediascorer(job, directory):
        """Execute the Ediascorer on a given Protein and ElectronDensityMap object

        :param job: Contains the input Protein and ElectronDensityMap for the Ediascorer run
        :type job: EdiaJob
        :param directory: Path to desired output directory
        :type directory: Path
        :raises CalledProcessError: If an error occurs during Ediascorer execution
        """
        protein_file = job.input_protein.write_temp()
        ligand_file = job.input_ligand.write_temp() \
            if job.input_ligand else job.input_protein.write_ligands_temp()

        args = [
            settings.BINARIES['ediascorer'],
            '--target', protein_file.name,
            '--densitymap', job.electron_density_map.file.path,
            '--outputfolder', str(directory.absolute())
        ]
        if ligand_file:
            args.extend(['--ligand', ligand_file.name])

        try:
            logger.info('Executing command line call: %s', " ".join(args))
            subprocess.check_call(args)
        except subprocess.CalledProcessError as error:
            # Diese beiden exit codes werden vom Ediascorer zurückgegeben, je nach dem
            # ob man das Programm mit oder ohne Liganden startet. In beiden Fällen
            # wird trotzdem Output produziert.
            # Error code 9: Continued with errors
            # Wird auf Mac zurückgegeben, wenn der ediascorer mit Liganden ausgeführt wird:
            # Error code 127: Noch unbekannt
            # Wird auf Mac zurückgegeben, wenn der ediascorer ohne Liganden ausgeführt wird
            if error.returncode not in frozenset([9, 127]):
                raise error

    @staticmethod
    def csv_to_dict(file):
        """Helper function for converting a csv file into a dict

        :param file: Path to the csv file
        :type file: Path
        :return: Dictionary containing the csv data
        :rtype: dict
        """
        data = {}
        with open(file, 'r', encoding='utf8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if 'Infile id' in row:
                    infile_id = row['Infile id']
                    data[infile_id] = row
                else:
                    # Structure scores may disappear at this point if they are not of ligands
                    # uniquely identified by the following structure name.
                    structure_name = row['Name'] + '_' + row['Chain'] + '_' + row['ID']
                    data[structure_name] = row
        return data

    @staticmethod
    def load_results(job, path):
        """Store the resulting pdb file and atom scores file as new objects in the database

        :param job: Job object where the resulting output objects will be stored
        :type job: EdiaJob
        :param path: Path to the output directory
        :type path: Path
        """
        EdiascorerWrapper.load_scored_protein(job, path)
        EdiascorerWrapper.load_edia_scores(job, path)
        load_processed_ligands(path, job.output_protein)
        job.save()

    @staticmethod
    def load_scored_protein(job, path):
        """Store the generated pdb file string in a new Protein database object

        :param job: Job object where the resulting output protein will be stored
        :type job: EdiaJob
        :param path: Path to the output directory
        :type path: Path
        :raises RuntimeError: If no pdb file was generated by the Ediascorer
        """
        pdb_files = list(path.glob('*.pdb'))
        if len(pdb_files) != 1:
            raise RuntimeError('Edia scorer: Error loading output file')
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

    @staticmethod
    def load_edia_scores(job, path):
        """Store the generated Edia scores csv file in a new EDIAScores database object

        :param job: Job object where the resulting output EDIAScores object will be stored
        :type job: EdiaJob
        :param path: Path to the output directory
        :type path: Path
        """
        atom_scores = EdiascorerWrapper.load_csv_data(path, '*atomscores.csv', )
        structure_scores = EdiascorerWrapper.load_csv_data(path, '*structurescores.csv')
        job.edia_scores = EdiaScores(
            atom_scores=atom_scores,
            structure_scores=structure_scores,
            parent_edia_job=job
        )
        job.edia_scores.save()
        job.save()

    @staticmethod
    def load_csv_data(path, glob_expression):
        """Loads CSV data of Edia results to dict

        :param path: Path to the output directory
        :type path: Path
        :param glob_expression: Expression to glob files from path
        :type glob_expression: str
        :return: Dictionary containing the csv data
        :rtype: dict
        :raises RuntimeError: If less or more than 1 csv file was generated by the Ediascorer
        """
        score_files = list(path.glob(glob_expression))
        if len(score_files) > 1:
            raise RuntimeError('Edia scorer: found more than one file for expression in output')
        if len(score_files) == 0:
            raise RuntimeError('Edia scorer: found no file for expression in output')
        score_file = score_files[0]
        return EdiascorerWrapper.csv_to_dict(score_file)

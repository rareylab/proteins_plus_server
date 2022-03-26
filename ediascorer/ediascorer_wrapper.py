"""A django model friendly wrapper around the edia scorer binary"""
import logging
import csv
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from molecule_handler.utils import load_processed_ligands
from molecule_handler.models import Protein
from ediascorer.models import AtomScores

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
        protein = job.input_protein

        with protein.write_temp() as protein_file, protein.write_ligands_temp() as ligand_file:
            args = [
                settings.BINARIES['ediascorer'],
                '--target', protein_file.name,
                '--densitymap', job.electron_density_map.file.path,
                '--outputfolder', str(directory.absolute())
            ]
            if ligand_file:
                args.extend(['--ligand', ligand_file.name])

            try:
                logger.debug('Executing command line call: %s', " ".join(args))
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
        with open(file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                infile_id = row['Infile id']
                data[infile_id] = row
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
        EdiascorerWrapper.load_atom_scores(job, path)
        load_processed_ligands(path, job.input_protein, job.output_protein)
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
    def load_atom_scores(job, path):
        """Store the generated atom scores csv file in a new AtomScores database object

        :param job: Job object where the resulting output AtomScores object will be stored
        :type job: EdiaJob
        :param path: Path to the output directory
        :type path: Path
        :raises RuntimeError: If no csv file was generated by the Ediascorer
        """
        atom_score_files = list(path.glob('*atomscores.csv'))
        if len(atom_score_files) > 1:
            raise RuntimeError('Edia scorer: found more than one atom score file in output')
        if len(atom_score_files) == 0:
            raise RuntimeError('Edia scorer: found no atom score file in output')
        atom_score_file = atom_score_files[0]

        atom_scores = AtomScores(
            scores=EdiascorerWrapper.csv_to_dict(atom_score_file)
        )
        atom_scores.save()

        job.atom_scores = atom_scores
        job.save()
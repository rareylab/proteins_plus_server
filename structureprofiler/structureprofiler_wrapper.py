"""A django model friendly wrapper around the StructureProfiler binary"""
import logging
import csv
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from django.conf import settings
from structureprofiler.models import StructureProfilerOutput
logger = logging.getLogger(__name__)


class StructureProfilerWrapper:
    """A django model friendly wrapper around the structureprofiler binary"""

    LIGAND_FIELDS = {
        'Name': ['name', 'str'],
        'HET-Code': ['HETCode', 'str'],
        'Chain': ['chain', 'str'],
        'ID': ['ID', 'str'],
        'Tests': ['ligandStructureProfilerTests', 'bool'],
        'VALUE Maximum atomic B factor': ['maxAtomBFactor', 'float'],
        'TEST RESULT Occupancy': ['noAltLocs', 'bool'],
        'TEST RESULT Crystal symmetry contacts': ['noCrystalContacts', 'bool'],
        'VALUE OWAB': ['OWAB', 'float'],
        'TEST RESULT Intramolecular clash': ['noIntramolecularClash', 'bool'],
        'TEST RESULT VSEPR bond angles': ['bondAnglesTest', 'bool'],
        'TEST RESULT Unusual bond lengths': ['bondLengthsTest', 'bool'],
        'TEST RESULT Torsion angles': ['torsionAnglesTest', 'bool'],
        'TEST RESULT Aromatic ring planarity': ['ringPlanarityTest', 'bool'],
        'VALUE Number of heavy atoms': ['heavyAtoms', 'int'],
        'VALUE Molecular weight': ['molecularWeight', 'float'],
        'VALUE Lipinski acceptors': ['lipinskiAcceptors', 'int'],
        'VALUE Lipinski donors': ['lipinskiDonors', 'int'],
        'VALUE LogP': ['logP', 'float'],
        'VALUE Number of peptide residues': ['nofPeptideResidues', 'int'],
        'VALUE Number of rotatable bonds': ['NROT', 'int'],
        'VALUE Number of stereo centers': ['stereoCenters', 'int'],
        'TEST RESULT SMARTS': ['SMARTSExklusionTest', 'bool'],
        'TEST RESULT HET code': ['HETExclusionTest', 'bool'],
        'VALUE EDIAm': ['EDIAm', 'float']
    }

    COMPLEX_FIELDS = {
        'Tests': ['complexStructureProfilerTests', 'bool'],
        'VALUE Resolution': ['resolution', 'float'],
        'VALUE DPI': ['DPI', 'float'],
        'VALUE R factor': ['rFactor', 'float'],
        'VALUE R free factor': ['rFree', 'float'],
        'TEST RESULT Overfitting': ['overfittingTest', 'bool'],
        'TEST RESULT Model significance': ['significanceTest', 'bool']
    }

    ACTIVE_SITE_FIELDS = {
        'Uniprot-IDs': ['uniprotID', 'str'],
        'Ligand': ['ligand', 'str'],
        'Chains': ['chains', 'str'],
        'Tests': ['activeSiteStructureProfilerTests', 'bool'],
        'TEST RESULT B factor ratio': ['bFactorRatioTest', 'bool'],
        'TEST RESULT Occupancy': ['noAltLocs', 'bool'],
        'TEST RESULT Intramolecular clash': ['noIntramolecularClash', 'bool'],
        'TEST RESULT Intermolecular clash': ['noIntermolecularClash', 'bool'],
        'TEST RESULT VSEPR bond angles': ['bondAnglesTest', 'bool'],
        'TEST RESULT Unusual bond lengths': ['bondLengthsTest', 'bool'],
        'TEST RESULT EDIAm per residue': ['residueEDIATest', 'bool']
    }

    @staticmethod
    def structureprofiler(job):
        """Run the Structureprofiler for a Protein object from the database.
        Create new Object instances for the results.

        :param job: Contains the input Protein and ElectronDensityMap for the StructureProfiler run
        :type job: StructureProfilerJob
        """
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)
            StructureProfilerWrapper.execute_structureprofiler(job, dir_path)
            StructureProfilerWrapper.load_results(job, dir_path)

    @staticmethod
    def execute_structureprofiler(job, dir_path):
        """Execute the Structureprofiler on a given Protein (and optional ElectronDensityMap object)

        :param job: Contains the input Protein for the StructureProfiler run
        :type job: StructureProfilerJob
        :param dir_path: Path to the output directory
        :type dir_path: Path
        :raises CalledProcessError: If an error occurs during StructureProfiler execution
        """

        protein_file = job.input_protein.write_temp()
        if job.input_ligand:
            ligand_file = job.input_ligand.write_temp()
        else:
            ligand_file = job.input_protein.write_ligands_temp()

        args = [
            settings.BINARIES['structureprofiler'],
            '--complex', protein_file.name,
            '--outputDir', str(dir_path.resolve())
        ]
        if job.electron_density_map:
            args.extend(['--density', job.electron_density_map.file.path])

        if ligand_file:
            args.extend(['--ligand', ligand_file.name])

        logger.debug('Executing command line call: %s', " ".join(args))
        subprocess.check_call(args)

    @staticmethod
    def data_collection(cast_to, key, data, row):
        """Helper function for converting ligand or active site data into dictionary
        :param cast_to: type used in data dict for given field
        :type cast_to: str
        :param key: Key used in data dict for given fields
        :type key: str
        :param data: dictionary with csv data up to current row
        :type data: dict
        :param row: row of csv file
        :type row: list
        :return data: Dictionary with added csv data of read row
        :rtype: dict
        """
        for i in range(2, len(row)):
            if row[i]:
                if cast_to == 'float':
                    data[i-1][key] = float(row[i])
                elif cast_to == 'int':
                    data[i-1][key] = int(row[i])
                elif cast_to == 'bool':
                    if row[i] == 'passed':
                        data[i-1][key] = True
                    else:
                        data[i-1][key] = False
                else:
                    data[i-1][key] = str(row[i])

        return data

    @staticmethod
    def complex_csv_to_dict(file):
        """Helper function for converting the complex csv file into a dict

        :param file: Path to the complex csv file
        :type file: Paths
        :return: Dictionary containing the csv data
        :rtype: dict
        """
        data = {}
        fields = StructureProfilerWrapper.COMPLEX_FIELDS

        with open(file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            for row in csv_reader:
                if row[0] in fields:
                    cast_to = fields[row[0]][1]
                    key = fields[row[0]][0]
                    if cast_to == 'float':
                        data[key] = float(row[-1])
                    elif cast_to == 'int':
                        data[key] = int(row[-1])
                    elif cast_to == 'bool':
                        if row[-1] == 'passed':
                            data[key] = True
                        else:
                            data[key] = False
                    else:
                        data[key] = str(row[-1])
        return data

    @staticmethod
    def active_site_csv_to_dict(file):
        """Helper function for converting the activesite csv file into a dict

        :param file: Path to the activesite csv file
        :type file: Paths
        :return: Dictionary containing the csv data
        :rtype: dict
        """
        data = {}
        fields = StructureProfilerWrapper.ACTIVE_SITE_FIELDS
        with open(file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            for row in csv_reader:
                if row[0] in fields:
                    cast_to = fields[row[0]][1]
                    key = fields[row[0]][0]
                    if not row[2]:
                        return data
                    if row[0] == 'Uniprot-IDs':
                        for i in range(1, len(row) - 1):
                            data[i] = {}
                    data = StructureProfilerWrapper.data_collection(cast_to, key, data, row)
        return data

    @staticmethod
    def ligand_csv_to_dict(file):
        """Helper function for converting the ligand csv file into a dict

        :param file: Path to the ligand csv file
        :type file: Paths
        :return: Dictionary containing the csv data
        :rtype: dict
        """

        data = {}
        fields = StructureProfilerWrapper.LIGAND_FIELDS
        with open(file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            for row in csv_reader:

                if row[0] in fields:
                    cast_to = fields[row[0]][1]
                    key = fields[row[0]][0]
                    if not row[2]:
                        return data
                    if row[0] == 'Name':
                        for i in range(1, len(row) - 1):
                            data[i] = {}
                    data = StructureProfilerWrapper.data_collection(cast_to, key, data, row)

        return data

    @staticmethod
    def load_results(job, path):
        """ Store the resulting csv files as new objects in the database

        :param job: Job object where the resulting output objects will be stored
        :type job: StructureProfilerJob
        :param path: Path to the output directory
        :type path: Path
        :raises RuntimeError: If at least one of the 3 output csv files missing
        """

        complex_files = list(path.glob('*Complex.csv'))
        if len(complex_files) > 1:
            raise RuntimeError('Structurprofiler: found more than one Complex file in output')
        if len(complex_files) == 0:
            raise RuntimeError('Structurprofiler: found no Complex file in output')
        complex_file = complex_files[0]
        complex_data = StructureProfilerWrapper.complex_csv_to_dict(complex_file)

        active_site_files = list(path.glob('*ActiveSites.csv'))
        if len(active_site_files) > 1:
            raise RuntimeError('Structureprofiler: found more than one ActiveSites file in output')
        if len(active_site_files) == 0:
            raise RuntimeError('Structurprofiler: found no ActiveSite file in output')
        active_site_file = active_site_files[0]
        active_site_data = StructureProfilerWrapper.active_site_csv_to_dict(active_site_file)

        ligand_files = list(path.glob('*Ligands.csv'))
        if len(ligand_files) > 1:
            raise RuntimeError('Structureprofiler: found more than one Ligands file in output')
        if len(ligand_files) == 0:
            raise RuntimeError('Structurprofiler: found no Ligands file in output')
        ligand_file = ligand_files[0]
        ligand_data = StructureProfilerWrapper.ligand_csv_to_dict(ligand_file)

        output_data = {
            'complex': complex_data,
            'active_sites': active_site_data,
            'ligands': ligand_data
        }

        output = StructureProfilerOutput(output_data=output_data, parent_structureprofiler_job=job)
        output.save()

        job.output_data = output
        job.save()

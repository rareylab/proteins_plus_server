"""Test for custom molecule handler commands"""
from django.core.management import call_command, CommandError
from proteins_plus.test.utils import PPlusTestCase
from ..models import PreprocessorJob, Protein, Ligand, ProteinSite, ElectronDensityMap
from .utils import create_successful_preprocessor_job, create_test_proteinsite,\
    create_test_electrondensitymap


class CommandsTests(PPlusTestCase):
    """Test for custom molecule handler commands"""

    def test_clean_molecule_data(self):
        """Test clean_molecule_data command cleans models and jobs"""
        preprocessor_job = create_successful_preprocessor_job()
        protein = preprocessor_job.output_protein
        ligand = protein.ligand_set.first()
        protein_site = create_test_proteinsite(protein)
        density_map = create_test_electrondensitymap()
        with self.settings(DEFAULT_JOB_CACHE_TIME=-1):
            call_command('clean_molecule_data')
        self.assertFalse(PreprocessorJob.objects.filter(id=preprocessor_job.id).exists())
        self.assertFalse(Protein.objects.filter(id=protein.id).exists())
        self.assertFalse(Ligand.objects.filter(id=ligand.id).exists())
        self.assertFalse(ProteinSite.objects.filter(id=protein_site.id).exists())
        self.assertFalse(ElectronDensityMap.objects.filter(id=density_map.id).exists())

    def test_download_pdb(self):
        """Test download_pdb command"""

        # Since a valid internet connection is necessary for download_pdb we
        # only do negative tests.
        self.assertRaises(CommandError, call_command, 'download_pdb', '--target_dir',
                          '/ThisIsA/VeryUnlikely/PathTo-Exist,isIt?42424242')

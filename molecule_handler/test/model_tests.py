"""tests for molecule_handler database models"""
import os
from pathlib import Path
from django.test import override_settings

from proteins_plus.test.utils import PPlusTestCase
from .config import TestConfig
from .utils import create_test_preprocessor_job, create_successful_preprocessor_job, \
    create_test_protein, create_test_ligand, create_test_proteinsite
from ..tasks import preprocess_molecule_task
from ..models import PreprocessorJob, Protein, Ligand, ProteinSite, ElectronDensityMap


class ModelTests(PPlusTestCase):
    """Database model tests"""

    def test_ligand_images(self):
        """Test creation and deletion of ligand images"""
        job = create_test_preprocessor_job()

        preprocess_molecule_task.run(job.id)
        job = PreprocessorJob.objects.get(pk=job.id)
        ligand = job.output_protein.ligand_set.first()
        image_path = ligand.image.path

        self.assertEqual(os.path.exists(image_path), True)
        ligand.delete()
        self.assertEqual(os.path.exists(image_path), False)

    def test_preprocessor_cache_behaviour(self):
        """Test storing and retrieving objects from cache"""
        job = create_test_preprocessor_job()
        job.set_hash_value()
        job.save()

        job2 = create_test_preprocessor_job()
        cached_job = job2.retrieve_job_from_cache()
        self.assertIsNotNone(cached_job)
        self.assertEqual(cached_job.id, job.id)

        job3 = PreprocessorJob(pdb_code=TestConfig.protein)
        cached_job = job3.retrieve_job_from_cache()
        self.assertIsNone(cached_job)

    def test_job_delete_cascade(self):
        """Test cascading deletion behavior of the preprocessor job"""
        job = create_successful_preprocessor_job()
        protein = job.output_protein
        job.delete()
        # deleting the job does not delete the protein
        self.assertTrue(Protein.objects.filter(id=protein.id).exists())

        job = create_successful_preprocessor_job()
        protein = job.output_protein
        protein.delete()
        # deleting the protein deletes the job
        self.assertFalse(PreprocessorJob.objects.filter(id=job.id).exists())

    def test_ligand_delete_cascade(self):
        """Test cascading deletion behavior of the protein"""
        protein = create_test_protein()
        ligand = create_test_ligand(protein)
        ligand.delete()
        # deleting the ligand does not delete the protein
        self.assertTrue(Protein.objects.filter(id=protein.id))

        protein = create_test_protein()
        ligand = create_test_ligand(protein)
        protein.delete()
        # deleting the protein deletes the ligand
        self.assertFalse(Ligand.objects.filter(id=ligand.id))

    def test_proteinsite_write_edf_temp(self):
        """Test writing and temporary EDF file for the ProteinSite model"""
        protein = create_test_protein()
        protein_site = create_test_proteinsite(protein=protein)
        protein_site.save()
        with protein.write_temp() as protein_file, \
                protein_site.write_edf_temp(protein_file.name) as edf_file:
            protein_site2 = ProteinSite.from_edf(protein, Path(edf_file.name))
            protein_site2.save()
            self.assertEqual(protein_site.protein, protein_site2.protein)
            self.assertEqual(protein_site.site_description, protein_site2.site_description)

    def test_protein_from_file(self):
        """Test building Protein model from file"""
        with open(TestConfig.protein_file, 'r', encoding='utf-8') as pdb_file:
            protein = Protein.from_file(pdb_file)
            self.assertIsNotNone(protein)
            pdb_file.seek(0)
            file_str = pdb_file.read()
            self.assertEqual(protein.file_string, file_str)
            self.assertEqual(protein.name, TestConfig.protein)
            self.assertIsNone(protein.pdb_code)
            self.assertIsNone(protein.uniprot_code)
            self.assertEqual(protein.file_type, 'pdb')
        with open(TestConfig.protein_file, 'r', encoding='utf-8') as pdb_file:
            protein = Protein.from_file(pdb_file, pdb_code='MyPDBCode', uniprot_code='MyUniCode')
            self.assertIsNotNone(protein)
            pdb_file.seek(0)
            file_str = pdb_file.read()
            self.assertEqual(protein.file_string, file_str)
            self.assertEqual(protein.name, 'MyPDBCode')
            self.assertEqual(protein.pdb_code, 'MyPDBCode')
            self.assertEqual(protein.uniprot_code, 'MyUniCode')
            self.assertEqual(protein.file_type, 'pdb')

    @override_settings(LOCAL_PDB_MIRROR_DIR=Path('test_files/'))
    def test_protein_from_pdb_code(self):
        """Test building Protein model from PDB code"""
        protein = Protein.from_pdb_code(TestConfig.protein)
        self.assertIsNotNone(protein)
        with open(TestConfig.protein_file, 'r', encoding='utf-8') as pdb_file:
            self.assertEqual(protein.file_string, pdb_file.read())
        self.assertEqual(protein.name, TestConfig.protein)
        self.assertEqual(protein.pdb_code, TestConfig.protein)
        self.assertIsNone(protein.uniprot_code)
        self.assertEqual(protein.file_type, 'pdb')

        # the same with uniprot code
        protein = Protein.from_pdb_code(TestConfig.protein, uniprot_code='MyUniCode')
        self.assertIsNotNone(protein)
        with open(TestConfig.protein_file, 'r', encoding='utf-8') as pdb_file:
            self.assertEqual(protein.file_string, pdb_file.read())
        self.assertEqual(protein.name, TestConfig.protein)
        self.assertEqual(protein.pdb_code, TestConfig.protein)
        self.assertEqual(protein.uniprot_code, 'MyUniCode')
        self.assertEqual(protein.file_type, 'pdb')

    def test_electrondensitymap_from_ccp4(self):
        """Test building ElectronDensityMap model from ccp4 file"""
        density_map = ElectronDensityMap.from_ccp4(TestConfig.density_file)
        self.assertIsNotNone(density_map)
        with open(TestConfig.density_file, 'rb') as density_file:
            self.assertEqual(density_file.read(), density_map.file.read())

    def test_protein_write_ligands_temp(self):
        """Test writing all Ligand models of a Protein model a temporary file"""
        # no ligand
        protein = create_test_protein()
        protein.save()
        ligand_file = protein.write_ligands_temp()
        self.assertIsNone(ligand_file)

        # two ligands
        protein = create_test_protein()
        ligand1 = create_test_ligand(protein, ligand_name=TestConfig.ligand,
                                     ligand_filepath=TestConfig.ligand_file)
        ligand1.save()
        ligand2 = create_test_ligand(protein, ligand_name=TestConfig.ligand2,
                                     ligand_filepath=TestConfig.ligand2_file)
        ligand2.save()
        protein.save()
        ligand_file = protein.write_ligands_temp()
        self.assertIsNotNone(ligand_file)
        self.assertTrue(ligand_file.name.endswith('.sdf'))
        file_str = ligand_file.read()
        self.assertEqual(file_str.split('\n').count('$$$$'), 2)

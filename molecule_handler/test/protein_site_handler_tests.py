"""tests for ProteinSiteHandler"""
from pathlib import Path
from tempfile import NamedTemporaryFile

from proteins_plus.test.utils import PPlusTestCase
from .config import TestConfig
from .utils import create_test_protein
from ..models import ProteinSite
from ..protein_site_handler import ProteinSiteHandler


class ProteinSiteHandlerTests(PPlusTestCase):
    """ProteinSiteHandler tests"""

    def test_proteinsite_to_and_from_edf(self):
        """Test reading and writing of proteinsite as edf string"""

        # test read/write of EDF
        protein = create_test_protein()
        protein_site = ProteinSite(protein=protein, site_description=TestConfig.site_json)
        protein_site.save()

        with protein.write_temp() as protein_file:
            edf_str = ProteinSiteHandler.proteinsite_to_edf(protein_site, protein_file.name)
            self.assertIsNotNone(edf_str)
            self.assertIsInstance(edf_str, str)
            self.assertGreater(len(edf_str), 0)
            with NamedTemporaryFile(mode='w') as edf_file:
                edf_file.write(edf_str)
                edf_file.seek(0)

                protein_site2 = ProteinSite.from_edf(protein, Path(edf_file.name))
                protein_site2.save()
                self.assertEqual(protein_site2.protein, protein_site.protein)
                self.assertEqual(protein_site2.site_description, protein_site.site_description)

    def test_proteinsite_to_and_from_edf_with_icodes(self):
        """Test reading and writing of proteinsite as edf string with iCodes"""

        # test iCode parsing in 1a3e
        protein = create_test_protein(protein_name=TestConfig.protein_1a3e,
                                       protein_filepath=TestConfig.protein_file_1a3e,
                                       pdb_code='1a3e')
        protein_site = ProteinSite.from_edf(protein, TestConfig.edf_file_1a3e)
        protein_site.save()
        self.assertIsNotNone(protein_site)
        self.assertEqual(protein, protein_site.protein)
        self.assertTrue('residue_ids' in protein_site.site_description.keys())
        self.assertIsNotNone(protein_site.site_description['residue_ids'])
        self.assertGreater(len(protein_site.site_description['residue_ids']), 0)

        with protein.write_temp() as protein_file:
            edf_str = ProteinSiteHandler.proteinsite_to_edf(protein_site, protein_file.name)
            self.assertIsNotNone(edf_str)
            self.assertIsInstance(edf_str, str)
            self.assertGreater(len(edf_str), 0)
            with NamedTemporaryFile(mode='w') as edf_file:
                edf_file.write(edf_str)
                edf_file.seek(0)

                protein_site2 = ProteinSite.from_edf(protein, Path(edf_file.name))
                protein_site2.save()
                self.assertEqual(protein_site2.protein, protein_site.protein)
                self.assertEqual(protein_site2.site_description, protein_site.site_description)

    def test_proteinsite_edf_specialcases(self):
        """Test special cases of EDF string"""

        protein = create_test_protein(protein_name=TestConfig.protein_1a3e,
                                       protein_filepath=TestConfig.protein_file_1a3e,
                                       pdb_code='1a3e')
        # test invalid EDF strings
        edf_invalid_missing_reference = "RESIDUE ALA A 1"
        with NamedTemporaryFile(mode='w') as edf_file:
            edf_file.write(edf_invalid_missing_reference)
            edf_file.seek(0)
            self.assertRaises(ValueError,
                              ProteinSite.from_edf, protein, Path(edf_file.name))
        edf_invalid_missing_position = "REFERENCE <MYPATH>\nRESIDUE ALA A "
        with NamedTemporaryFile(mode='w') as edf_file:
            edf_file.write(edf_invalid_missing_position)
            edf_file.seek(0)
            self.assertRaises(ValueError,
                              ProteinSite.from_edf, protein, Path(edf_file.name))

        # test multiple EDF entries (we ignore all but the first)
        edf_multiple = "REFERENCE <MYPATH>\nRESIDUE ALA A 1\nREFERENCE <MYPATH1>\nRESIDUE ALA A 2\n"
        with NamedTemporaryFile(mode='w') as edf_file:
            edf_file.write(edf_multiple)
            edf_file.seek(0)
            protein_site = ProteinSite.from_edf(protein, Path(edf_file.name))
            protein_site.save()
            self.assertEqual(protein, protein_site.protein)
            self.assertTrue('residue_ids' in protein_site.site_description.keys())
            self.assertIsNotNone(protein_site.site_description['residue_ids'])
            self.assertEqual(len(protein_site.site_description['residue_ids']), 1)

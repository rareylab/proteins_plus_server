"""Test for custom proteins plus commands"""
from pathlib import Path
from django.core.management import call_command
from django.contrib.staticfiles.testing import LiveServerTestCase
from molecule_handler.tasks import preprocess_molecule_task
from molecule_handler.test.utils import create_test_preprocessor_job


class CommandsTests(LiveServerTestCase):
    """Test for custom proteins plus commands"""

    def test_server_check(self):
        """Test the check server command"""
        # ensure schema.yml exists
        if not Path('schema.yml').exists():
            call_command('spectacular', '--file', 'schema.yml')

        # ensure a ligand with an image exists
        job = create_test_preprocessor_job()
        preprocess_molecule_task.run(job.id)

        call_command('check_server', self.live_server_url)

    def test_server_check_no_ligand(self):
        """Test the check server command without a ligand in the database"""
        # ensure schema.yml exists
        if not Path('schema.yml').exists():
            call_command('spectacular', '--file', 'schema.yml')

        call_command('check_server', self.live_server_url)

"""Django friendly wrapper of Poseview"""
import logging
import os
import subprocess
from tempfile import NamedTemporaryFile

from proteins_plus import settings

logger = logging.getLogger(__name__)


class PoseviewWrapper:
    """Django friendly wrapper of Poseview"""

    @staticmethod
    def poseview(job):
        """Execute Poseview and load the results

        :param job: Poseview job
        :type job: PoseviewJob
        """
        image = PoseviewWrapper.execute_poseview(job)
        job.image.save(os.path.basename(image.name), image)

    @staticmethod
    def execute_poseview(job):
        """Execute Poseview

        :param job: Poseview Job
        :type job: poseview.models.PoseviewJob
        :return: generated image
        :rtype: NamedTemporaryFile
        """
        image = NamedTemporaryFile(mode='rb', suffix='.svg')  # pylint: disable=consider-using-with
        with job.input_protein.write_temp() as protein_file:
            with job.input_ligand.write_temp() as ligand_file:
                # run command in Poseview directory (necessary for licensing)
                poseview_basename = os.path.basename(settings.BINARIES['poseview'])
                args = [
                    './' + poseview_basename,
                    '-p', protein_file.name,
                    '-l', ligand_file.name,
                    '-t', '',  # don't write text to the image
                    '-o', image.name
                ]
                logger.info('Executing command line call: %s', " ".join(args))
                poseview_directory = os.path.dirname(settings.BINARIES['poseview'])
                subprocess.check_call(args, stdout=subprocess.DEVNULL, cwd=poseview_directory)
        return image

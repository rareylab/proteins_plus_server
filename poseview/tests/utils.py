"""Poseview testing utils"""
import os
from django.core.files import File
from proteins_plus.models import Status
from molecule_handler.models import Protein, Ligand
from ..models import PoseviewJob
from .config import TestConfig


def create_poseview_job():
    """Create a Poseview job

    :return: Poseview Job
    :rtype: PoseviewJob
    """
    with open(TestConfig.protein_file, encoding='utf8') as protein_file:
        input_protein = Protein.from_file(protein_file)
    input_protein.save()
    with open(TestConfig.ligand_file, encoding='utf8') as ligand_file:
        input_ligand = Ligand.from_file(ligand_file, input_protein)
    input_ligand.save()

    job = PoseviewJob(input_protein=input_protein, input_ligand=input_ligand)
    job.save()
    return job


def create_successful_poseview_job():
    """Create a successful Poseview job

    :return: successful Poseview Job
    :rtype: PoseviewJob
    """
    job = create_poseview_job()
    with open(TestConfig.result_image, 'rb') as result_image:
        job.image.save(os.path.basename(TestConfig.result_image), File(result_image))
    job.status = Status.SUCCESS
    job.save()
    return job

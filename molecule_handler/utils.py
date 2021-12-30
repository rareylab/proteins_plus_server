"""Helper functions for handling molecule data"""
from django.core.files import File
from .models import Ligand


def load_processed_ligands(path, input_protein, output_protein):
    """Extract Ligand objects from multi sdf file after execution of a job.

    :param path: Path the output directory of the job
    :type path: Path
    :param input_protein: Input Protein object of the executed job
    :type input_protein: Protein
    :param output_protein: Output Protein object of the executed job
    :type output_protein: Protein
    :raises RuntimeError: If more than one sdf file is found in the output directory
    """
    sd_files = list(path.glob('*.sdf'))
    if len(sd_files) > 1:
        raise RuntimeError('Job Error: Too many sdf files found in output directory')
    if len(sd_files) == 1:
        with sd_files[0].open() as ligand_file:
            multi_ligand_string = ligand_file.read()
        ligand_strings = multi_ligand_string.split('$$$$\n')
        for ligand_string in ligand_strings:
            if ligand_string == '' or ligand_string.isspace():
                continue
            ligand_name = ligand_string.split('\n')[0]

            ligand = Ligand(
                name=ligand_name,
                file_type='sdf',
                file_string=ligand_string + '$$$$',
                protein=output_protein
            )

            # TODO: Check if new images were created. If so, connect them to the ligand objects
            # instead of the old images.
            old_ligand = input_protein.ligand_set.get(name=ligand_name)
            if old_ligand.image:
                new_image = f'{ligand.name}_{ligand.id}.png'
                ligand.image.save(new_image, File(old_ligand.image.open('rb')))

            ligand.save()

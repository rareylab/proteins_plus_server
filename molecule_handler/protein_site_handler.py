"""Class that handles conversion of protein sites"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ProteinSiteHandler:
    """Handles conversion of different representations of protein sites

    - The backend communicates protein site descriptions with NAOMI-tools using EDF. This
      means the backend provides EDF files as input to NAOMI-tools and the backend reads
      output EDF files from NAOMI-tools.
    - The same protein site descriptions are communicated between user and backend using
      JSON. The frontend/REST API can provide JSON files of describing protein sites.
    - Within the backend protein site descriptions are stored as ProteinSite models in
      the database.

    Example workflows are:
        - User triggers NAOMI-tool -> EDF -> JSON -> ProteinSite-Model in DB -> JSON to User
            - This would be the workflow of DoGSite
        - User sends JSON -> ProteinSite-Model in DB -> EDF -> NAOMI-tool
            - This would be the workflow with SIENA.
        Obviously, the first and the second workflow can be executed subsequently.
    """

    @staticmethod
    def edf_to_json(edf_path):
        """Convert an EDF file to JSON-like dict.

        note:: Reference protein path in EDF file will be ignored.
        :param edf_path: File path to EDF file.
        :type edf_path: pathlib.Path
        :return: A JSON-like dict containing the site description from the EDF file.
        :rtype: dict
        """
        reference = None
        site_dict = {'residue_ids': []}
        with open(edf_path, 'r') as edf_file:
            for line in edf_file:
                if line.startswith('REFERENCE'):
                    if reference is not None:
                        logger.warning('More than one entry in EDF file. Ignoring all but first!')
                        break
                    reference = line.split('REFERENCE ')[1].strip()
                elif line.startswith('RESIDUE'):
                    if reference is None:
                        raise ValueError('Invalid EDF file. REFERENCE is missing')
                    splits = line.strip().split(' ')
                    if len(splits) != 4 and len(splits) != 5:
                        raise ValueError('Invalid EDF file. Can not parse RESIDUE line')
                    position = splits[3]
                    if len(splits) == 5:
                        position += splits[4]
                    site_dict['residue_ids'].append(
                        {'name': splits[1], 'chain': splits[2], 'position': position})
        return site_dict

    @staticmethod
    def proteinsite_to_edf(proteinsite, reference_protein_path):
        """Converts ProteinSite instance to an EDF (ensemble data file) string.

        :param proteinsite: The ProteinSite model instance.
        :type proteinsite: The ProteinSite.
        :param reference_protein_path: File path to reference protein.
        :type reference_protein_path: pathlib.Path
        :return: The EDF string.
        :rtype: str
        """
        residue_strings = []
        residues_dict_list = proteinsite.site_description['residue_ids']
        for residue_dict in residues_dict_list:
            position_str = ""
            if residue_dict['position'][-1].isalpha():
                # the position string includes an iCode
                for i in reversed(range(len(residue_dict['position']))):
                    if not residue_dict['position'][i].isalpha():
                        position_str = \
                            f'{residue_dict["position"][:i + 1]} {residue_dict["position"][i + 1:]}'
                        break
            else:
                position_str = residue_dict["position"]
            residue_strings.append(
                f'RESIDUE {residue_dict["name"]} {residue_dict["chain"]} {position_str}')

        newline = '\n'
        edf_str = f"""# EDF Format to define binding site and ensemble.
# Lines starting with a '#' character are considered as comments.
# Use the REFERENCE line to define a reference protein.
# This line is also considered as the beginning of a new ensemble entry.

REFERENCE {Path(reference_protein_path).resolve()}

# Use RESIDUE lines to define the residues of the query binding site.
# Please use the residue's name, it's chain identifier and the serial number
# as specified in the REFERENCE PDB file to define a residue that should be part
# of the query. Additional 'insertion codes' in the REFERENCE PDB file must also
# be specified here. Please use the following order:
# RESIDUE residueName chainIdentifier serialNumber <insertion code>

{newline.join(residue_strings)}
"""
        return edf_str

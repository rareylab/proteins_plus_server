import os
import re

PDB_CODE_PATTERN = re.compile(r'^[0-9][a-zA-Z0-9]{3}$')
UNIPROT_PATTERN = re.compile(r'^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$')


def valid_protein_extension(protein_file):
    ext = os.path.splitext(protein_file.name)[1]
    return ext == '.pdb'


def valid_ligand_extension(ligand_file):
    ext = os.path.splitext(ligand_file.name)[1]
    return ext == '.sdf'


def valid_pdb_code(pdb_code):
    return PDB_CODE_PATTERN.match(pdb_code)


def valid_uniprot_code(uniprot_code):
    return UNIPROT_PATTERN.match(uniprot_code)

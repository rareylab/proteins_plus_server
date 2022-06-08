"""ediascorer api views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from molecule_handler.models import Protein, Ligand, ElectronDensityMap

from .models import EdiaScores, EdiaJob
from .tasks import ediascore_protein_task
from .serializers import EdiaJobSerializer, EdiaScoresSerializer, \
    EdiascorerSubmitSerializer


class EdiascorerView(APIView):
    """View for executing the EDIAscorer"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=EdiascorerSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer,
    )
    def post(self, request):
        """Start an EDIAscorer job.

        The EDIAscorer calculates atom-wise electron density support scores. To calculate score the
        EDIAscorer requires an electron density map, which can be either retrieved with a PDB code
        or explicitly uploaded. If a ligand file is uploaded it will be added to the
        "structure_scores" of the EDIA scores object.

        Required:
         - either "protein_file" or "protein_id" for the protein structure.
         - either "pdb_code" or "electron_density_map" (file) for the electron density.

        Optional:
         - custom "ligand_file" to add ligands

        *Estimating Electron Density Support for Individual Atoms and Molecular Fragments in
        X-ray Structures
        Agnes Meyder, Eva Nittinger, Gudrun Lange, Robert Klein, and Matthias Rarey
        Journal of Chemical Information and Modeling 2017 57 (10), 2437-2447*
        """
        serializer = EdiascorerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        if request_data['protein_id']:
            input_protein = Protein.objects.get(id=request_data['protein_id'])
        else:
            input_protein = Protein.from_file(
                request_data['protein_file'], pdb_code=request_data['pdb_code'])
            input_protein.save()
        if request_data['ligand_file']:
            if request_data['protein_id']:
                # remove id so that input protein will be copied
                input_protein.id = None
                input_protein.save()
            ligand = Ligand.from_file(request_data['ligand_file'], input_protein)
            ligand.save()
        input_protein.save()

        job = EdiaJob(input_protein=input_protein)
        job.save()

        if request_data['electron_density_map'] is not None:
            electron_density_map = ElectronDensityMap()
            electron_density_map.file.save(
                request_data['electron_density_map'].name,
                request_data['electron_density_map'].file
            )
            electron_density_map.save()
            job.electron_density_map = electron_density_map
        elif request_data['pdb_code'] is not None:
            job.density_file_pdb_code = request_data['pdb_code']
        else:
            job.density_file_pdb_code = input_protein.pdb_code

        job_id, retrieved = submit_task(job, ediascore_protein_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer({
            'job_id': job_id,
            'retrieved_from_cache': retrieved
        })
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class EdiaJobViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all EDIAscorer jobs"""
    queryset = EdiaJob.objects.all()
    serializer_class = EdiaJobSerializer


class EdiaScoresViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all EDIA scores objects"""
    queryset = EdiaScores.objects.all()
    serializer_class = EdiaScoresSerializer

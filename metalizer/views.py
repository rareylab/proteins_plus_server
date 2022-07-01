"""Metalizer Views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from molecule_handler.models import Protein

from .serializers import MetalizerJobSerializer, MetalizerJobSubmitSerializer, \
    MetalizerInfoSerializer
from .models import MetalizerJob, MetalizerInfo
from .tasks import metalize_task


class MetalizerView(APIView):
    """Metalizer submission API"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=MetalizerJobSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer
    )
    def post(self, request):
        """Start a METALizer job

        METALizer predicts the coordination geometry of metals in metalloproteins. Provide
        a protein structure and a metal in the structure to obtain a list of the most likely
        geometric coordination of the metal atom.

        Required:
         - either "protein_id" or "protein_file"
         - "residue_id" Residue number of the metal.
         - "chain_id" Chain identifier of the metal.
         - "name" Name of the metal.

        Optional:
         - "distance_threshold" cutoff for atoms considered coordination partners (N,O,S,Cl).

         *Schöning-Stierand K., Diedrich K., Fährrolfes R., Flachsenberg F.,
          Meyder A., Nittinger E., Steinegger R., Rarey M.,
          ProteinsPlus: interactive analysis of protein–ligand binding interfaces,
          Nucleic Acids Research, Volume 48, Issue W1, 2020, Pages W48-W53*
        """
        serializer = MetalizerJobSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        if request_data['protein_id']:
            input_protein = Protein.objects.get(id=request_data['protein_id'])
        else:
            input_protein = Protein.from_file(request_data['protein_file'])
            input_protein.save()

        job = MetalizerJob(
            input_protein=input_protein,
            residue_id=request_data['residue_id'],
            chain_id=request_data['chain_id'],
            name=request_data['name'],
            distance_threshold=request_data['distance_threshold']
        )
        job.save()

        job_id, retrieved = submit_task(job, metalize_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer({
            'job_id': job_id,
            'retrieved_from_cache': retrieved
        })
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class MetalizerJobViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Metalizer job views"""
    queryset = MetalizerJob.objects.all()
    serializer_class = MetalizerJobSerializer


class MetalizerInfoViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Metalizer info views"""
    queryset = MetalizerInfo.objects.all()
    serializer_class = MetalizerInfoSerializer

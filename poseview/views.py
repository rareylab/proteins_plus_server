"""Poseview Views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from molecule_handler.models import Protein, Ligand

from .models import PoseviewJob
from .serializers import PoseviewJobSerializer, PoseviewJobSubmitSerializer
from .tasks import poseview_task


class PoseviewView(APIView):
    """Poseview submission API"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=PoseviewJobSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer
    )
    def post(self, request):
        """Start a PoseView job.

        PoseView generates projections of protein-ligand interactions to 2D images. The ligand
        specified by either "ligand_file" or "ligand_id" will be used to define the binding site
        and the protein-ligand interactions.

        Required:
         - either "protein_file" or "protein_id"
         - either "ligand_file" or "ligand_id"

        *Stierand, K., Rarey, M. PoseView -- molecular interaction patterns at a glance.
        J Cheminform 2, P50 (2010).*
        """
        serializer = PoseviewJobSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        if request_data['protein_id']:
            input_protein = Protein.objects.get(id=request_data['protein_id'])
        else:
            input_protein = Protein.from_file(request_data['protein_file'])
            input_protein.save()

        if request_data['ligand_id']:
            input_ligand = Ligand.objects.get(id=request_data['ligand_id'])
            # create a new protein ligand pair if both are not associated already
            if not input_protein.ligand_set.filter(id=input_ligand.id).exists():
                input_protein.id = None
                input_protein.save()
                input_ligand.id = None
                input_ligand.protein = input_protein
                input_ligand.save()
        else:
            # copy the protein to not modify the original
            if request_data['protein_id']:
                input_protein.id = None
                input_protein.save()
            input_ligand = Ligand.from_file(request_data['ligand_file'], input_protein)
            input_ligand.save()

        job = PoseviewJob(input_protein=input_protein, input_ligand=input_ligand)
        job.save()
        job_id, retrieved = submit_task(job, poseview_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer({
            'job_id': job_id,
            'retrieved_from_cached': retrieved
        })
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class PoseviewJobViewSet(ReadOnlyModelViewSet):
    """Retrieve specific or list all PoseView jobs"""
    queryset = PoseviewJob.objects.all()
    serializer_class = PoseviewJobSerializer

"""DoGSite Views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from molecule_handler.models import Ligand, Protein

from .serializers import DoGSiteJobSerializer, DoGSiteJobSubmitSerializer, \
    DoGSiteInfoSerializer
from .models import DoGSiteJob, DoGSiteInfo
from .tasks import dogsite_task


class DoGSiteView(APIView):
    """DoGSite submission API"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=DoGSiteJobSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer
    )
    def post(self, request):
        """Post new DoGSite job"""
        serializer = DoGSiteJobSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        if request_data['protein_id']:
            input_protein = Protein.objects.get(id=request_data['protein_id'])
        else:
            input_protein = Protein.from_file(request_data['protein_file'])
            input_protein.save()

        input_ligand = None
        if request_data['ligand_id']:
            input_ligand = Ligand.objects.get(id=request_data['ligand_id'])
        elif request_data['ligand_file']:
            input_ligand = Ligand.from_file(request_data['ligand_file'], input_protein)
            input_ligand.save()

        calc_subpockets = False
        if request_data['calc_subpockets']:
            calc_subpockets = request_data['calc_subpockets']

        ligand_bias = False
        if request_data['ligand_bias']:
            ligand_bias = request_data['ligand_bias']

        if request_data['chain_id']:
            job = DoGSiteJob(
                input_protein=input_protein,
                input_ligand=input_ligand,
                chain_id=request_data['chain_id'],
                calc_subpockets=calc_subpockets,
                ligand_bias=ligand_bias
            )
        else:
            job = DoGSiteJob(
                input_protein=input_protein,
                input_ligand=input_ligand,
                calc_subpockets=calc_subpockets,
                ligand_bias=ligand_bias
            )
        job.save()

        job_id, retrieved = submit_task(job, dogsite_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer({
            'job_id': job_id,
            'retrieved_from_cache': retrieved
        })
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class DoGSiteJobViewSet(ReadOnlyModelViewSet):
    """DoGSite job views"""
    queryset = DoGSiteJob.objects.all()
    serializer_class = DoGSiteJobSerializer


class DoGSiteInfoViewSet(ReadOnlyModelViewSet):
    """DoGSite info views"""
    queryset = DoGSiteInfo.objects.all()
    serializer_class = DoGSiteInfoSerializer

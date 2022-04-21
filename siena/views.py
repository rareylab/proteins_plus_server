"""siena api views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from molecule_handler.models import Protein, Ligand, ProteinSite

from .models import SienaJob, SienaInfo
from .tasks import siena_protein_task
from .serializers import SienaJobSerializer, SienaSubmitSerializer, SienaInfoSerializer


class SienaView(APIView):
    """View for executing the siena"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=SienaSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer
    )
    def post(self, request):
        """API endpoint for executing the siena binary

        :param request: Http request containing the job data. Structure of
                        request.data is given by the SienaSubmitSerializer
        :type request: HttpRequest
        :return: Http Response indicating a successful submission or any errors.
        :rtype: HttpResponse
        """
        serializer = SienaSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        # handle the different input variations
        input_protein = None
        input_ligand = None
        input_site = None
        if request_data['protein_id']:
            input_protein = Protein.objects.get(id=request_data['protein_id'])
        else:
            input_protein = Protein.from_file(request_data['protein_file'])
            input_protein.save()
            if request_data['ligand_file']:
                input_ligand = Ligand.from_file(request_data['ligand_file'], input_protein)
                input_ligand.save()
        if input_ligand is None:
            if request_data['ligand_id']:
                input_ligand = Ligand.objects.get(id=request_data['ligand_id'])
            elif request_data['protein_site_id']:
                input_site = ProteinSite.objects.get(id=request_data['protein_site_id'])
            else:
                site_json = request_data['protein_site_json']
                input_site = ProteinSite(protein=input_protein, site_description=site_json)
                input_site.save()

        # create the job with input values
        if input_ligand is not None:
            job = SienaJob(input_protein=input_protein, input_ligand=input_ligand)
        else:
            job = SienaJob(input_protein=input_protein, input_site=input_site)
        job.save()

        # submit the job
        job_id, retrieved = submit_task(job, siena_protein_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer({
            'job_id': job_id,
            'retrieved_from_cache': retrieved
        })
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class SienaJobViewSet(ReadOnlyModelViewSet):
    """Siena job views"""
    queryset = SienaJob.objects.all()
    serializer_class = SienaJobSerializer


class SienaInfoViewSet(ReadOnlyModelViewSet):
    """Siena info views"""
    queryset = SienaInfo.objects.all()
    serializer_class = SienaInfoSerializer

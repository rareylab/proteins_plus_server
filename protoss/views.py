"""protoss api views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from molecule_handler.models import Protein
from .models import ProtossJob
from .serializers import ProtossJobSerializer, ProtossSubmitSerializer
from .tasks import protoss_protein_task

class ProtossView(APIView):
    """View for protossing Protein objects in the database"""
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request=ProtossSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer,
    )
    def post(self, request):
        """API endpoint for protossing protein objects in the database

        :param request: Http request containing the job data. Structure of
                        request.data is given by the ProtossSubmitSerializer
        :type request: HttpRequest
        :return: Http Response indicating a successful submission or any errors.
        :rtype: HttpResponse
        """
        serializer = ProtossSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        input_protein = Protein.objects.get(id=request_data['protein_id'])

        job = ProtossJob(input_protein=input_protein)

        response_data = submit_task(job, protoss_protein_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer(response_data)

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class ProtossJobViewSet(ReadOnlyModelViewSet): # pylint: disable=too-many-ancestors
    """Viewset for retrieving specifiv or listing all ProtossJob instances from database"""
    queryset = ProtossJob.objects.all()
    serializer_class = ProtossJobSerializer

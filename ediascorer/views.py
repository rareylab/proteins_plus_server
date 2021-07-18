"""ediascorer api views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.common import JobSubmitResponseSerializer
from molecule_handler.models import Protein, ElectronDensityMap

from .models import AtomScores, EdiaJob
from .tasks import ediascore_protein_task
from .serializers import EdiaJobSerializer, AtomScoresSerializer,\
                            EdiascorerSubmitSerializer

class EdiascorerView(APIView):
    """View for executing the Ediascorer"""
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request=EdiascorerSubmitSerializer,
        responses=JobSubmitResponseSerializer
    )
    def post(self, request):
        """API endpoint for executing the ediascorer binary

        :param request: Http request containing the job data. Structure of
                        request.data is given by the EdiascorerSubmitSerializer
        :type request: HttpRequest
        :return: Http Response indicating a successful submission or any errors.
        :rtype: HttpResponse
        """
        serializer = EdiascorerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        input_protein = Protein.objects.get(id=request_data['protein_id'])

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
        job.save()

        ediascore_protein_task.delay(job.id)

        response_data = {'job_id': job.id}
        serializer = JobSubmitResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class EdiaJobViewSet(ReadOnlyModelViewSet): # pylint: disable=too-many-ancestors
    """Viewset for retrieving specific or listing all EdiaJob objects"""
    queryset = EdiaJob.objects.all()
    serializer_class = EdiaJobSerializer

class AtomScoresViewSet(ReadOnlyModelViewSet): # pylint: disable=too-many-ancestors
    """Viewset for retrieving specific or listing all AtomScores objects"""
    queryset = AtomScores.objects.all()
    serializer_class = AtomScoresSerializer

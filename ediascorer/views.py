"""ediascorer api views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from molecule_handler.tasks import preprocess_molecule_task
from molecule_handler.models import Protein, ElectronDensityMap, PreprocessorJob

from .models import AtomScores, EdiaJob
from .tasks import ediascore_protein_task
from .serializers import EdiaJobSerializer, AtomScoresSerializer, \
    EdiascorerSubmitSerializer


class EdiascorerView(APIView):
    """View for executing the Ediascorer"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=EdiascorerSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer
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

        if request_data['protein_id']:
            input_protein = Protein.objects.get(id=request_data['protein_id'])
        else:
            preprocess_job = PreprocessorJob.from_file(
                request_data['protein_file'], request_data['ligand_file'])
            job_id, retrieved = submit_task(
                preprocess_job,
                preprocess_molecule_task,
                request_data['use_cache'],
                immediate=True
            )
            preprocess_job = PreprocessorJob.objects.get(id=job_id)
            input_protein = preprocess_job.output_protein
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
    """Viewset for retrieving specific or listing all EdiaJob objects"""
    queryset = EdiaJob.objects.all()
    serializer_class = EdiaJobSerializer


class AtomScoresViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Viewset for retrieving specific or listing all AtomScores objects"""
    queryset = AtomScores.objects.all()
    serializer_class = AtomScoresSerializer

"""GeoMine Views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task

from .serializers import GeoMineJobSerializer, GeoMineJobSubmitSerializer, GeoMineInfoSerializer
from .models import GeoMineJob, GeoMineInfo
from .tasks import geomine_task


class GeoMineView(APIView):
    """GeoMine submission API"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)
 
    @extend_schema(
        request=GeoMineJobSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer
    )
    def post(self, request):
        """Post new GeoMine job"""
        serializer = GeoMineJobSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        job = GeoMineJob(
            filter_file=request_data['filter_file']
        )
        job.save()

        job_id, retrieved = submit_task(job, geomine_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer({
            'job_id': job_id,
            'retrieved_from_cache': retrieved
        })
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class GeoMineJobViewSet(ReadOnlyModelViewSet):
    """GeoMine job views"""
    queryset = GeoMineJob.objects.all()
    serializer_class = GeoMineJobSerializer


class GeoMineInfoViewSet(ReadOnlyModelViewSet):
    """GeoMine info views"""
    queryset = GeoMineInfo.objects.all()
    serializer_class = GeoMineInfoSerializer

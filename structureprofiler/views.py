"""structureprofiler api views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from molecule_handler.models import Protein, ElectronDensityMap, Ligand

from .models import StructureProfilerOutput, StructureProfilerJob
from .tasks import structureprofiler_protein_task
from .serializers import StructureProfilerJobSerializer, StructureProfilerOutputSerializer, \
    StructureProfilerSubmitSerializer


class StructureProfilerView(APIView):
    """View for executing the StructureProfiler"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=StructureProfilerSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer
    )
    def post(self, request):
        """API endpoint for executing the structureprofiler_binary

        StructureProfiler is a tool for automatic, objective and customizable
        profiling of X-ray protein structures based on the most frequently
        applied selection criteria currently in use to assemble benchmark datasets.
        To do so the StructureProfiler requires a protein file. If an electron density map
        (as file or PDB code) is uploaded the StructureProfiler additionaly
        includes filter criteria depending on EDIAscorer.

        Required:
         - either "protein_file" or "protein_id"

        Optional:
         - custom "ligand_file" to add specific ligands
         - either "pdb_code" or "electron_density_map" (file)

        *StructureProfiler: an all-in-one tool for 3D protein structure profiling
        Meyder A, Kampen S, Sieg J, Fährrolfes R, Friedrich NO, Flachsenberg F, Rarey M.
        Bioinformatics. 2019 Mar 1;35(5):874-876
        doi: 10.1093/bioinformatics/bty692 PMID: 30124779*
        """
        serializer = StructureProfilerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        if request_data['protein_id']:
            input_protein = Protein.objects.get(id=request_data['protein_id'])
        else:
            input_protein = Protein.from_file(request_data['protein_file'])
            input_protein.save()

        if request_data['ligand_file']:
            if request_data['protein_id']:
                input_protein.id = None
                input_protein.save()
            ligand = Ligand.from_file(request_data['ligand_file'], input_protein)
            ligand.save()
            job = StructureProfilerJob(input_protein=input_protein, input_ligand=ligand)
        else:
            job = StructureProfilerJob(input_protein=input_protein)

        if request_data['electron_density_map']:
            electron_density_map = ElectronDensityMap()
            electron_density_map.file.save(
                request_data['electron_density_map'].name,
                request_data['electron_density_map'].file
            )
            electron_density_map.save()
            job.electron_density_map = electron_density_map
            job.save()

        elif request_data['pdb_code']:
            job.density_file_pdb_code = request_data['pdb_code']
            job.save()

        job_id, retrieved = submit_task(
            job, structureprofiler_protein_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer({
            'job_id': job_id,
            'retrieved_from_cache': retrieved
        })
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class StructureProfilerJobViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Viewset for retrieving specific or listing all StructureProfiler objects"""
    queryset = StructureProfilerJob.objects.all()
    serializer_class = StructureProfilerJobSerializer


class StructureProfilerOutputViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Viewset for retrieving specific or listing all StructureProfilerOutput objects"""
    queryset = StructureProfilerOutput.objects.all()
    serializer_class = StructureProfilerOutputSerializer

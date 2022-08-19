"""molecule_handler api views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from .models import Protein, Ligand, ProteinSite, ElectronDensityMap, PreprocessorJob, \
    PreprocessorJobData
from .serializers import ProteinSerializer, LigandSerializer, ProteinSiteSerializer, \
    ElectronDensityMapSerializer, PreprocessorJobSerializer, UploadSerializer, \
    PreprocessorJobDataSerializer
from .tasks import preprocess_molecule_task


class ProteinUploadView(APIView):
    """View for uploading proteins and ligands"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=UploadSerializer,
        responses=ProteinsPlusJobResponseSerializer,
    )
    def post(self, request):
        """Upload proteins and ligands.

        Uploading proteins and ligands will preprocess them. Ligands will be detected in protein
        files, separated into ligand models, and 2D representation will be generated for these
        ligands. Uploaded ligands will override any ligands present in a PDB entry or a protein
        file.

        Required:
         - either "protein_file", "pdb_code" or "uniprot_code" (for AlphaFold predicted structure)

        Optional:
         - custom "ligand_file" to override ligands
        """
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        job = PreprocessorJob()
        job.pdb_code = request_data['pdb_code']
        job.uniprot_code = request_data['uniprot_code']
        job.save()
        assert job.id is not None, 'never make new PreprocessorJobData with not saved job model'
        input_data = PreprocessorJobData(parent_preprocessor_job=job)
        if request_data['protein_file']:
            input_data.input_protein_string = request_data['protein_file'].file.read().decode(
                'utf8')
        if request_data['ligand_file']:
            input_data.input_ligand_string = request_data['ligand_file'].file.read().decode(
                'utf8')
        input_data.save()
        job.input_data = input_data
        job.save()

        job_id, retrieved = submit_task(job, preprocess_molecule_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer({
            'job_id': job_id,
            'retrieved_from_cache': retrieved
        })
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class ProteinViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all proteins"""
    queryset = Protein.objects.all()
    serializer_class = ProteinSerializer


class LigandViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all ligands"""
    queryset = Ligand.objects.all()
    serializer_class = LigandSerializer


class ProteinSiteViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all ProteinSite"""
    queryset = ProteinSite.objects.all()
    serializer_class = ProteinSiteSerializer


class ElectronDensityMapViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all electron density maps"""
    queryset = ElectronDensityMap.objects.all()
    serializer_class = ElectronDensityMapSerializer


class PreprocessorJobDataViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve the specific or list of all the preprocessor job input data"""
    queryset = PreprocessorJobData.objects.all()
    serializer_class = PreprocessorJobDataSerializer


class PreprocessorJobViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all preprocessor jobs"""
    queryset = PreprocessorJob.objects.all()
    serializer_class = PreprocessorJobSerializer

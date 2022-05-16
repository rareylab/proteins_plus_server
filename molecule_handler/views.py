"""molecule_handler api views"""
import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from .models import Protein, Ligand, ProteinSite, ElectronDensityMap, PreprocessorJob
from .serializers import ProteinSerializer, LigandSerializer, ProteinSiteSerializer, \
    ElectronDensityMapSerializer, PreprocessorJobSerializer, UploadSerializer
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
         - either "pdb_code" or "protein_file"

        Optional:
         - custom "ligand_file" to override ligands
        """
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data

        pdb_code = request_data['pdb_code']
        uniprot_code = request_data['uniprot_code']
        protein_name = pdb_code
        protein_string = None
        ligand_string = None

        if request_data['protein_file']:
            protein_string = request_data['protein_file'].file.read().decode('utf8')
            protein_name = os.path.basename(request_data['protein_file'].name)
            protein_name = os.path.splitext(protein_name)[0]
        if request_data['ligand_file']:
            ligand_string = request_data['ligand_file'].file.read().decode('utf8')

        job = PreprocessorJob(
            protein_name=protein_name,
            pdb_code=pdb_code,
            uniprot_code=uniprot_code,
            protein_string=protein_string,
            ligand_string=ligand_string
        )

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
    """Viewset for retrieving specific or listing all ProteinSite instances from database"""
    queryset = ProteinSite.objects.all()
    serializer_class = ProteinSiteSerializer


class ElectronDensityMapViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all electron density maps"""
    queryset = ElectronDensityMap.objects.all()
    serializer_class = ElectronDensityMapSerializer


class PreprocessorJobViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all preprocessor jobs"""
    queryset = PreprocessorJob.objects.all()
    serializer_class = PreprocessorJobSerializer

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
    """View for executing DoGSite"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=DoGSiteJobSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer
    )
    def post(self, request):
        """Start a DoGSite job

        DoGSite detects and describes binding sites which can then easily be visualized. It is a
        grid-based method that uses a Difference of Gaussian filter to detect potential binding
        pockets based on the 3D structure of the protein. Global properties, describing the size,
        shape and chemical features of the predicted (sub)pockets are calculated automatically.

        Required:
         - either "protein_file" or "protein_id" for the protein structure.

        Optional:
         - either "ligand_file" or "ligand_id" for calculating ligand coverage of a pocket.
         - "calc_subpockets" to output also subpockets (parts of pockets).
         - "ligand_bias" to use the provided ligand to extend pockets to fully cover the ligand.
         - "chain_id" to focus binding site prediction on a single chain only.

        *Analyzing the Topology of Active Sites: On the Prediction of Pockets and Subpockets
         Andrea Volkamer, Axel Griewel, Thomas Grombacher, and Matthias Rarey
         Journal of Chemical Information and Modeling 2010 50 (11), 2041-2052*
        """
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
    """Retrieve specific or list of DoGSite jobs"""
    queryset = DoGSiteJob.objects.all()
    serializer_class = DoGSiteJobSerializer


class DoGSiteInfoViewSet(ReadOnlyModelViewSet):
    """Retrieve specific or list of DoGSite result info objects"""
    queryset = DoGSiteInfo.objects.all()
    serializer_class = DoGSiteInfoSerializer

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
        """Start a Siena job.

        Siena searches for similar binding sites in the Protein Data Bank (PDB). Provide a protein
        structure as input and a query binding site by either uploading a ligand as reference or
        a list of residues making up the binding site. Siena returns a list of similar binding sites
        as an superposed structural ensemble. Siena can be used to investigate similar binding
        pockets, structural variability and different ligands binding in the same or similar
        pockets.

        Required:
         - either "protein_file" or "protein_id"

        Optional:
         - either "ligand_file" or "ligand_id" to define the query binding site.
         - either "protein_site_id" or "protein_site_json" to define the query binding site.

        *Stefan Bietz and Matthias Rarey Journal of Chemical Information and Modeling 2016 56 (1),
         248-259*
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
    """Retrieve specific or list all Siena job"""
    queryset = SienaJob.objects.all()
    serializer_class = SienaJobSerializer


class SienaInfoViewSet(ReadOnlyModelViewSet):
    """Retrieve specific or list all Siena result info objects"""
    queryset = SienaInfo.objects.all()
    serializer_class = SienaInfoSerializer

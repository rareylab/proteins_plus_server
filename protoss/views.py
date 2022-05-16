"""protoss api views"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task
from molecule_handler.models import Protein, Ligand
from .models import ProtossJob
from .serializers import ProtossJobSerializer, ProtossSubmitSerializer
from .tasks import protoss_protein_task


class ProtossView(APIView):
    """View for protossing Protein objects in the database"""
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    @extend_schema(
        request=ProtossSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer,
    )
    def post(self, request):
        """Start a Protoss job.

        Protoss predicts hydrogen positions for proteins. If there are ligands associated with a
        protein these are used in the calculation. Uploading a custom ligand file will remove
        clashing ligands in the protein.

        Required:
         - either "protein_id" or "protein_file"

        Optional:
         - custom "ligand_file"

         *Protoss: A holistic approach to predict tautomers and protonation states in protein-ligand complexes
         Stefan Bietz and Sascha Urbaczek and Benjamin Schulz and Matthias Rarey
         Journal of Cheminformatics vol. 6, no. 1, p. 12, 2014*
        """
        serializer = ProtossSubmitSerializer(data=request.data)
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
            job = ProtossJob(input_protein=input_protein, input_ligand=ligand)
        else:
            job = ProtossJob(input_protein=input_protein)

        job_id, retrieved = submit_task(job, protoss_protein_task, request_data['use_cache'])
        serializer = ProteinsPlusJobResponseSerializer({
            'job_id': job_id,
            'retrieved_from_cache': retrieved
        })
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class ProtossJobViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Retrieve specific or list all Protoss jobs"""
    queryset = ProtossJob.objects.all()
    serializer_class = ProtossJobSerializer

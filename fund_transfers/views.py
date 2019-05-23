from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import FundTransfer
from .serializers import FundTransferSerializer


class FundTransfersList(generics.ListCreateAPIView):
    queryset = FundTransfer.objects.all()

    permission_classes = [IsAuthenticated]

    serializer_class = FundTransferSerializer


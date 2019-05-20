from rest_framework import views, generics
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *


class UserCreate(views.APIView):
    '''
    User creation view
    '''

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            serialized_data = serializer.data
            serialized_data['password'] = ''
            return Response(serialized_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountProductList(generics.ListAPIView):
    queryset = AccountProduct.objects.all()
    serializer_class = AccountProductSerializer


class AccountList(generics.ListCreateAPIView):
    pass
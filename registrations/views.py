from rest_framework import views, generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from drf_multiple_model.views import ObjectMultipleModelAPIView

from .serializers import *
from .permissions import *


class GeneralInfoAPIView(ObjectMultipleModelAPIView):
    '''
    General info multiple view for unauthenticated access
    Shows both Account Products and Currencies info
    '''
    querylist = [
        {'queryset': AccountProduct.objects.all(), 'serializer_class': AccountProductSerializer},
        {'queryset': Currency.objects.all(), 'serializer_class': CurrencySerializer},
    ]


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


class AccountProductList(generics.ListCreateAPIView):
    queryset = AccountProduct.objects.all()
    serializer_class = AccountProductSerializer

    permission_classes = [IsSuperUserOrReadOnly]


class AccountProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountProduct.objects.all()
    serializer_class = AccountProductSerializer

    permission_classes = [IsSuperUser]


class CurrencyList(generics.ListCreateAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    permission_classes = [IsSuperUserOrReadOnly]


class CurrencyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    permission_classes = [IsSuperUser]


class CustomerList(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    permission_classes = [IsAdminUser]


class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    permission_classes = [IsAdminUser]





class AccountList(generics.ListCreateAPIView):
    pass

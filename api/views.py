from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from api.models import Wallet, Customer
from api.serializer import CustomerSerializer, WalletSerializer, TransactionSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes


@authentication_classes([])
@permission_classes([])
@method_decorator(csrf_exempt, name="dispatch")
class WalletCreateAPIView(generics.ListCreateAPIView):
    """To create an account as well as getting the token for the other API endpoints."""

    def get_serializer_class(self):
        return CustomerSerializer

    def post(self, request,  *args, **kwargs):
        """Overriding the POST method"""
        serializer = CustomerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            customer_xid = serializer.validated_data['customer_xid']
            if Customer.objects.filter(customer_xid=customer_xid).first():
                customer = Customer.objects.filter(customer_xid=customer_xid).get()
                Wallet.objects.create(owned_by=customer)
                token = Token.objects.filter(user=customer).first()

                return Response({"token": token.key, "status": "success"},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class WalletEnableAPIView(generics.ListCreateAPIView):
    """To Enable the wallet."""
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        return WalletSerializer

    def get_queryset(self):
        return Wallet.objects.filter(owned_by=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class WalletDepositAPI(generics.ListCreateAPIView):
    """To deposit and withdraw money."""

    def get_serializer_class(self):
        return TransactionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "transaction": "deposit"})
        return context


class WalletWithdrawAPI(generics.ListCreateAPIView):
    """To deposit and withdraw money."""

    def get_serializer_class(self):
        return TransactionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request, "transaction": "withdraw"})
        return context
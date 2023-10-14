from functools import partial

from apps.base.models import ClientTransaction
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from ....mixins import SerializersMixin
from ....permissions import IsAcceptedContract, IsAccessToTheSection
from ...serializers import (ClientTransactionNotSafeSerializer,
                            ClientTransactionSafeSerializer)


class ClientTransactionViewSet(
    SerializersMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    safe_serializer = ClientTransactionSafeSerializer
    not_safe_serializer = ClientTransactionNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'clients'))

    def get_queryset(self):
        client = self.request.GET.get('client')
        partner = self.request.user.get_partner()

        params = {'client__partner__id': partner.id}
        transactions = ClientTransaction.objects.filter(**params)

        if client:
            transactions = transactions.filter(client__id=client)

        return transactions.all().select_related(
            'client',
            'client__wallet',
            'client__wallet__cert',
            'client__status',
        )

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_201_CREATED)

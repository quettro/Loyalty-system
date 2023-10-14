from functools import partial

from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet

from ...mixins import SerializersMixin
from ...permissions import IsAcceptedContract, IsAccessToTheSection
from ..serializers import WalletNotSafeSerializer, WalletSafeSerializer


class WalletViewSet(SerializersMixin, ModelViewSet):
    safe_serializer = WalletSafeSerializer
    not_safe_serializer = WalletNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'wallets'))

    def get_queryset(self):
        return self.request.user.get_partner().wallets.select_related('cert')

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'status': True})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.clients.count() > 0:
            raise APIException(('Нельзя удалить данный шаблон карты, т.к '
                                'к этому шаблону привязаны клиенты.'))

        instance.softdelete()
        return Response({'status': True}, status=HTTP_204_NO_CONTENT)

from functools import partial

from rest_framework import mixins
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from ....mixins import SerializersMixin
from ....permissions import IsAcceptedContract, IsAccessToTheSection
from ...serializers import ClientNotSafeSerializer, ClientSafeSerializer


class ClientViewSet(
    SerializersMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    safe_serializer = ClientSafeSerializer
    not_safe_serializer = ClientNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'clients'))

    def get_queryset(self):
        return self.request.user.get_partner().clients.all().select_related(
            'wallet', 'wallet__cert', 'status')

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.is_deleted:
            raise APIException(('Нельзя редактировать данные клиента, '
                                'т.к клиент удалил свою карту.'))

        super().update(request, *args, **kwargs)
        return Response({'status': True})

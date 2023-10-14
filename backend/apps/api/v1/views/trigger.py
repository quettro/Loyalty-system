from functools import partial

from apps.base.models import Trigger
from django.db.models import ProtectedError
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet

from ...mixins import SerializersMixin
from ...permissions import IsAcceptedContract, IsAccessToTheSection
from ..serializers import TriggerNotSafeSerializer, TriggerSafeSerializer


class TriggerViewSet(SerializersMixin, ModelViewSet):
    safe_serializer = TriggerSafeSerializer
    not_safe_serializer = TriggerNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'triggers'))

    def get_queryset(self):
        return Trigger.objects.filter(
            wallet__partner__id=self.request.user.get_partner().id
        ).select_related('wallet')

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'status': True})

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
        except ProtectedError:
            raise APIException(('Данную триггерную рассылку невозможно '
                                'удалить, т.к триггерная рассылка имеет '
                                'связанные записи.'))
        return Response({'status': True}, status=HTTP_204_NO_CONTENT)

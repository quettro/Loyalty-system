from functools import partial

from apps.base.models import Audience
from django.db.models import ProtectedError
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet

from ...mixins import SerializersMixin
from ...permissions import IsAcceptedContract, IsAccessToTheSection
from ..serializers import AudienceNotSafeSerializer, AudienceSafeSerializer


class AudienceViewSet(SerializersMixin, ModelViewSet):
    safe_serializer = AudienceSafeSerializer
    not_safe_serializer = AudienceNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'audiences'))

    def get_queryset(self):
        return Audience.objects.filter(
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
            raise APIException(('Данную аудиторию невозможно удалить, '
                                'т.к аудитория имеет связанные записи.'))
        return Response({'status': True}, status=HTTP_204_NO_CONTENT)

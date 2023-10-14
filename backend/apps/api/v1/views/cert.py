from functools import partial

from django.db.models import ProtectedError
from rest_framework import mixins
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from ...permissions import IsAcceptedContract, IsAccessToTheSection
from ..serializers import CertSerializer


class CertViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    serializer_class = CertSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'certs'))

    def get_queryset(self):
        return self.request.user.get_partner().certs.all()

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
        except ProtectedError:
            raise APIException(('Данный сертификат невозможно удалить, '
                                'т.к сертификат имеет связанные записи.'))
        return Response({'status': True}, status=HTTP_204_NO_CONTENT)

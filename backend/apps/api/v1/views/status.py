from functools import partial

from apps.base.models import Status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet

from ...mixins import SerializersMixin
from ...permissions import IsAcceptedContract, IsAccessToTheSection
from ..serializers import StatusNotSafeSerializer, StatusSafeSerializer


class StatusViewSet(SerializersMixin, ModelViewSet):
    safe_serializer = StatusSafeSerializer
    not_safe_serializer = StatusNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'statuses'))

    def get_queryset(self):
        wallet = self.request.GET.get('wallet')
        partner = self.request.user.get_partner()
        statuses = Status.objects.filter(wallet__partner__id=partner.id)

        if wallet:
            statuses = statuses.filter(wallet__id=wallet)

        return statuses.select_related('wallet', 'wallet__cert')

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'status': True})

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_204_NO_CONTENT)

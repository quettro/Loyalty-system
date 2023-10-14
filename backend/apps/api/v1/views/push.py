from functools import partial

from apps.base.models import Push
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from ...mixins import SerializersMixin
from ...permissions import IsAcceptedContract, IsAccessToTheSection
from ..serializers import PushNotSafeSerializer, PushSafeSerializer


class PushViewSet(
    SerializersMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    safe_serializer = PushSafeSerializer
    not_safe_serializer = PushNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'push'))

    def get_queryset(self):
        return Push.objects.filter(
            wallet__partner__id=self.request.user.get_partner().id
        ).select_related(
            'wallet', 'wallet__cert'
        )

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_201_CREATED)

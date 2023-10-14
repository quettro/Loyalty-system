from functools import partial

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet

from ...mixins import SerializersMixin
from ...permissions import IsAcceptedContract, IsAccessToTheSection
from ..serializers import EmployeeNotSafeSerializer, EmployeeSafeSerializer


class EmployeeViewSet(SerializersMixin, ModelViewSet):
    safe_serializer = EmployeeSafeSerializer
    not_safe_serializer = EmployeeNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'employees'))

    def get_queryset(self):
        return self.request.user.get_partner().employees.all().select_related(
            'user'
        ).prefetch_related('permissions')

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'status': True})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.user.delete()
        return Response({'status': True}, status=HTTP_204_NO_CONTENT)

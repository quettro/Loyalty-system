from functools import partial

from apps.base.models import Service
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet

from ....mixins import SerializersMixin
from ....permissions import IsAcceptedContract, IsAccessToTheSection
from ...serializers import ServiceNotSafeSerializer, ServiceSafeSerializer


class ServiceViewSet(SerializersMixin, ModelViewSet):
    safe_serializer = ServiceSafeSerializer
    not_safe_serializer = ServiceNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'services'))

    def get_queryset(self):
        category = self.request.GET.get('category')
        partner = self.request.user.get_partner()

        params = {'category__wallet__partner__id': partner.id}
        services = Service.objects.filter(**params)

        if category:
            services = services.filter(category__id=category)

        return services.all().select_related(
            'category',
            'category__wallet',
            'category__wallet__cert'
        )

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'status': True})

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'status': True}, status=HTTP_204_NO_CONTENT)

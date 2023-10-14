from functools import partial

from apps.base.models import ProductCategory
from django.db.models import ProtectedError
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet

from ....mixins import SerializersMixin
from ....permissions import IsAcceptedContract, IsAccessToTheSection
from ...serializers import (ProductCategoryNotSafeSerializer,
                            ProductCategorySafeSerializer)


class ProductCategoryViewSet(SerializersMixin, ModelViewSet):
    safe_serializer = ProductCategorySafeSerializer
    not_safe_serializer = ProductCategoryNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'products'))

    def get_queryset(self):
        wallet = self.request.GET.get('wallet')
        partner = self.request.user.get_partner()

        params = {'wallet__partner__id': partner.id}
        categories = ProductCategory.objects.filter(**params)

        if wallet:
            categories = categories.filter(wallet__id=wallet)

        return categories.all().select_related('wallet', 'wallet__cert')

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
            raise APIException(('Данную категорию невозможно удалить, '
                                'т.к категория имеет связанные записи.'))
        return Response({'status': True}, status=HTTP_204_NO_CONTENT)

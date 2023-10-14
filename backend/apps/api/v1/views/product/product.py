from functools import partial

from apps.base.models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet

from ....mixins import SerializersMixin
from ....permissions import IsAcceptedContract, IsAccessToTheSection
from ...serializers import ProductNotSafeSerializer, ProductSafeSerializer


class ProductViewSet(SerializersMixin, ModelViewSet):
    safe_serializer = ProductSafeSerializer
    not_safe_serializer = ProductNotSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'products'))

    def get_queryset(self):
        category = self.request.GET.get('category')
        partner = self.request.user.get_partner()

        params = {'category__wallet__partner__id': partner.id}
        products = Product.objects.filter(**params)

        if category:
            products = products.filter(category__id=category)

        return products.all().select_related(
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

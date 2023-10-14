from apps.base.models import Wallet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (  # isort: skip
    ConnectNotSafeSerializer,
    ConnectVerificationNotSafeSerializer
)


class ConnectMixin(APIView):
    wallet = None

    def get_wallet(self, request, *args, **kwargs):
        objects = Wallet.objects.not_deleted()
        objects = objects.select_related('partner__tariff', 'cert')
        self.wallet = get_object_or_404(objects, uuid=kwargs.get('uuid'))


class ConnectViewSet(ConnectMixin, APIView):
    permission_classes = []
    http_method_names = ('get', 'post',)
    serializer_class = ConnectNotSafeSerializer

    def get(self, request, *args, **kwargs):
        self.get_wallet(request, *args, **kwargs)

        return Response({
            'name': self.wallet.name,
            'logotype': self.wallet.logotype.url,
            'background_color': self.wallet.frontend['background_color'],
            'type': self.wallet.get_type_dict()
        })

    def post(self, request, *args, **kwargs):
        self.get_wallet(request, *args, **kwargs)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.registration(self.wallet)
        return Response({'path': instance.pkpass.url})


class ConnectVerificationViewSet(ConnectMixin, APIView):
    permission_classes = []
    http_method_names = ('post',)
    serializer_class = ConnectVerificationNotSafeSerializer

    def post(self, request, *args, **kwargs):
        self.get_wallet(request, *args, **kwargs)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.verification(request, self.wallet.partner)
        return Response({'token': instance.token})

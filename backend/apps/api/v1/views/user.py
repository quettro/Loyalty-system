from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (  # isort: skip
    CustomUserSerializer,
    ContractSafeSerializer,
    PermissionSerializer,
    TariffSafeSerializer
)


class UserViewSet(APIView):
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        permissions = user.get_permissions()
        partner = user.get_partner()

        context = {
            'user': CustomUserSerializer(user).data,
            'permissions': PermissionSerializer(permissions, many=True).data,
            'tariff': TariffSafeSerializer(partner.tariff).data
        }

        if user.is_partner:
            context['partner'] = {}

            if partner.is_contract:
                context['partner']['contract'] = {
                    'information': ContractSafeSerializer(
                        partner.contract.contract
                    ).data,
                    'accepted_at': partner.contract.created_at
                }

            context['partner']['balance'] = partner.balance

        return Response(context)

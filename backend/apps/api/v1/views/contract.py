from apps.base.utils import get_client_ip
from apps.documents.models import AcceptedContract, Contract
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from user_agents import parse

from ...permissions import IsPartner
from ..serializers import ContractSafeSerializer


class ContractViewSet(APIView):
    http_method_names = ('get', 'post',)
    permission_classes = (IsAuthenticated, IsPartner,)

    def get(self, request, *args, **kwargs):
        contract = Contract.objects.first()

        if contract is None:
            return Response({
                'contract': {}
            }, status=status.HTTP_204_NO_CONTENT)

        return Response({
            'contract': ContractSafeSerializer(
                contract
            ).data
        })

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.first()
        partner = request.user.partner

        if contract is None:
            return Response({
                'status': False
            }, status=status.HTTP_204_NO_CONTENT)

        if not partner.is_contract:
            user_agent = request.META.get('HTTP_USER_AGENT')
            user_agent = parse(user_agent)

            AcceptedContract.objects.create(
                contract=contract,
                partner=partner,
                ip=get_client_ip(request),
                browser_family=user_agent.browser.family,
                browser_version=user_agent.browser.version_string,
                os_family=user_agent.os.family,
                os_version=user_agent.os.version_string,
                device_family=user_agent.device.family,
                device_brand=user_agent.device.brand,
                device_model=user_agent.device.model
            )

            return Response({
                'status': True
            }, status=status.HTTP_201_CREATED)

        return Response({'status': True})

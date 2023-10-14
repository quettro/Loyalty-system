from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from ...permissions import IsAcceptedContract, IsPartner
from ..serializers import PartnerTransactionSafeSerializer


class PartnerTransactionViewSet(ReadOnlyModelViewSet):
    serializer_class = PartnerTransactionSafeSerializer
    permission_classes = (IsAuthenticated, IsPartner, IsAcceptedContract,)

    def get_queryset(self):
        return self.request.user.partner.transactions.all()

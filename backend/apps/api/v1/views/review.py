from functools import partial

from apps.base.models import Review
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from ...permissions import IsAcceptedContract, IsAccessToTheSection
from ..serializers import ReviewSafeSerializer


class ReviewViewSet(ReadOnlyModelViewSet):
    serializer_class = ReviewSafeSerializer

    permission_classes = (
        IsAuthenticated, IsAcceptedContract, partial(
            IsAccessToTheSection, 'reviews'))

    def get_queryset(self):
        partner = self.request.user.get_partner()

        return Review.objects.select_related(
            'client',
            'client__wallet',
            'client__wallet__cert',
            'client__status'
        ).filter(client__partner__id=partner.id)

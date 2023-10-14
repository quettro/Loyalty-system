from apps.base.models import Client, ClientTransaction
from django.db import models
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...permissions import IsAcceptedContract
from ..serializers import DashboardNotSafeSerializer


class DashboardViewSet(APIView):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated, IsAcceptedContract,)
    serializer_class = DashboardNotSafeSerializer

    def post(self, request, *args, **kwargs):
        context = {'request': request}
        serializer = self.serializer_class(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)

        filters = self.__get_filters(request, serializer.validated_data)
        clients = Client.objects.filter(**filters)
        ids = list(clients.values_list('id', flat=True))

        statistics = {
            'clients': {
                **clients.aggregate(count=models.Count('id'))
            },

            'transactions': {
                **clients.aggregate(
                    count=models.Count(
                        'transactions',
                        filter=models.Q(transactions__amount__gt=0)
                    )
                ),

                **clients.aggregate(
                    amount=models.Sum(
                        'transactions__amount',
                        filter=models.Q(transactions__amount__gt=0)
                    ),

                    avg=models.Avg(
                        'transactions__amount',
                        filter=models.Q(transactions__amount__gt=0)
                    )
                )
            }
        }

        return Response({**statistics, 'visits': self.__get_visits(ids)})

    def __get_visits(self, ids):
        visits = [0]

        transactions = list(
            ClientTransaction.objects.filter(
                amount__gt=0, client__id__in=ids
            ).values_list('created_at', flat=True)
        )[::-1]

        if len(transactions) > 1:
            visits = []

            for i in range(1, len(transactions)):
                visits.append((transactions[i] - transactions[i - 1]).days)

        return round(sum(visits) / len(visits))

    def __get_filters(self, request, validated_data):
        filters = {'partner__id': request.user.get_partner().id}

        if validated_data.get('wallet'):
            filters['wallet__id'] = validated_data['wallet'].id

        if validated_data.get('from_date') and validated_data.get('to_date'):
            filters['created_at__date__range'] = (
                validated_data['from_date'], validated_data['to_date'],)

        return filters

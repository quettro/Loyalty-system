from apps.base.models import Tariff
from rest_framework import serializers


class TariffSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff

        exclude = (
            'partner',
            'permissions',
            'is_use_push_for_geolocation',
            'push_limits',
            'is_use_api',
            'api_requests_limits',
            'is_use_sms',
            'is_use_sending_cards_by_sms',
            'discounts',
        )

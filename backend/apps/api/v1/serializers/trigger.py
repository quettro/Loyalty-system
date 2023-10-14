from apps.base.models import Trigger
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .audience import AudienceSafeSerializer
from .wallet import WalletSafeSerializer

from ...fields import (  # isort: skip
    CurrentPartnerAudiencesPrimaryKeyRelatedField,
    CurrentPartnerWalletsPrimaryKeyRelatedField
)


class TriggerSafeSerializer(serializers.ModelSerializer):
    wallet = WalletSafeSerializer()
    audience = AudienceSafeSerializer(c_exclude=['wallet'])

    class Meta:
        model = Trigger
        fields = '__all__'


class TriggerNotSafeSerializer(serializers.ModelSerializer):
    wallet = CurrentPartnerWalletsPrimaryKeyRelatedField()
    audience = CurrentPartnerAudiencesPrimaryKeyRelatedField()

    class Meta:
        model = Trigger
        fields = '__all__'

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

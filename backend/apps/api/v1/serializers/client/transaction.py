from apps.base.models import ClientTransaction
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ....fields import CurrentPartnerClientsPrimaryKeyRelatedField
from .client import ClientSafeSerializer


class ClientTransactionSafeSerializer(serializers.ModelSerializer):
    client = ClientSafeSerializer()

    class Meta:
        model = ClientTransaction
        exclude = ('is_auto_add_bonuses',)


class ClientTransactionNotSafeSerializer(serializers.ModelSerializer):
    client = CurrentPartnerClientsPrimaryKeyRelatedField()

    class Meta:
        model = ClientTransaction
        fields = '__all__'

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

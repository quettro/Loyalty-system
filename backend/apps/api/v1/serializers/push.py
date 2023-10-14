from apps.base.models import Push
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ...fields import CurrentPartnerWalletsPrimaryKeyRelatedField
from .wallet import WalletSafeSerializer


class PushSafeSerializer(serializers.ModelSerializer):
    wallet = WalletSafeSerializer()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Push
        exclude = ('task_id', 'is_send_immediately',)

    def get_status(self, obj):
        return obj.get_status_dict()


class PushNotSafeSerializer(serializers.ModelSerializer):
    wallet = CurrentPartnerWalletsPrimaryKeyRelatedField()

    class Meta:
        model = Push
        exclude = ('task_id', 'status',)

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

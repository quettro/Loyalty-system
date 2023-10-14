from apps.base.models import Audience
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ...fields import CurrentPartnerWalletsPrimaryKeyRelatedField
from .wallet import WalletSafeSerializer


class AudienceSafeSerializer(serializers.ModelSerializer):
    wallet = WalletSafeSerializer()
    sex = serializers.SerializerMethodField()
    device = serializers.SerializerMethodField()

    class Meta:
        model = Audience
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        c_exclude = kwargs.pop('c_exclude', [])

        if c_exclude:
            for key in c_exclude:
                self.fields.pop(key, None)

        super().__init__(*args, **kwargs)

    def get_sex(self, obj):
        return obj.get_sex().dict()

    def get_device(self, obj):
        return obj.get_device().dict()


class AudienceNotSafeSerializer(serializers.ModelSerializer):
    wallet = CurrentPartnerWalletsPrimaryKeyRelatedField()

    class Meta:
        model = Audience
        fields = '__all__'

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

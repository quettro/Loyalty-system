from apps.base.models import Wallet
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .cert import CertSerializer

from ...fields import (  # isort: skip
    CurrentPartnerCertsPrimaryKeyRelatedField,
    CurrentPartnerHiddenField
)


class WalletSafeSerializer(serializers.ModelSerializer):
    cert = CertSerializer()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        exclude = ('partner', 'deleted_at',)

    def get_type(self, obj):
        return obj.get_type_dict()


class WalletNotSafeSerializer(serializers.ModelSerializer):
    partner = CurrentPartnerHiddenField()
    cert = CurrentPartnerCertsPrimaryKeyRelatedField()

    class Meta:
        model = Wallet
        exclude = ('deleted_at',)

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Wallet.objects.all(),
                fields=('partner', 'name',),
                message='Карта с таким наименованием уже существует.'
            ),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.context['view'].action in ('update', 'partial_update',):
            self.fields.get('type').read_only = True
            self.fields.get('cert').read_only = True

    def validate(self, attrs):
        type = attrs.get('type')

        if type is not None:
            df = {
                Wallet.Type.DISCOUNT: (
                    Wallet.BONUS_FIELDS + Wallet.CHOP_FIELDS),

                Wallet.Type.BONUS: (
                    Wallet.DISCOUNT_FIELDS + Wallet.CHOP_FIELDS),

                Wallet.Type.CHOP: (
                    Wallet.DISCOUNT_FIELDS + Wallet.BONUS_FIELDS)
            }

            if type in df:
                for key in df[type]:
                    attrs.pop(key, None)

        return super().validate(attrs)

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

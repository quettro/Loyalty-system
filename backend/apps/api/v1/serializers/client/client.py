from apps.base.models import Client
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ..status import StatusSafeSerializer
from ..wallet import WalletSafeSerializer

from ....fields import (  # isort: skip
    CurrentPartnerHiddenField,
    CurrentPartnerWalletsPrimaryKeyRelatedField
)


class ClientSafeSerializer(serializers.ModelSerializer):
    wallet = WalletSafeSerializer()
    status = StatusSafeSerializer(c_exclude=['wallet'])
    sex = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = Client
        exclude = ('partner', 'authentication_token', 'pkpass',)

    def __init__(self, *args, **kwargs):
        c_exclude = kwargs.pop('c_exclude', [])

        if c_exclude:
            for key in c_exclude:
                self.fields.pop(key, None)

        super().__init__(*args, **kwargs)

    def get_sex(self, obj):
        return obj.get_sex_dict()

    def get_phone(self, obj):
        return obj.get_phone()


class ClientNotSafeSerializer(serializers.ModelSerializer):
    partner = CurrentPartnerHiddenField()
    wallet = CurrentPartnerWalletsPrimaryKeyRelatedField()
    status = serializers.HiddenField(default=None)

    class Meta:
        model = Client

        exclude = (
            'authentication_token',
            'numbers',
            'pkpass',
            'is_welcome_bonuses_received',
            'deleted_at',
        )

        extra_kwargs = {
            'name': {'required': True},
            'balance': {'required': True}
        }

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Client.objects.all(),
                fields=('wallet', 'phone',),
                message=(
                    'Клиент с таким номером телефона уже получал данную карту.'
                )
            ),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.context['view'].action in ('update', 'partial_update',):
            setattr(self.Meta, 'validators', {})

            self.fields.get('wallet').read_only = True
            self.fields.get('status').read_only = True
            self.fields.get('phone').read_only = True

    def validate(self, attrs):
        wallet = attrs.get('wallet')

        if wallet and 'status' in attrs:
            attrs['status'] = wallet.statuses.filter(
                is_by_default=True
            ).first()

        return super().validate(attrs)

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

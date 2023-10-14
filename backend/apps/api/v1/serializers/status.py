from apps.base.models import Status
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ...fields import CurrentPartnerWalletsPrimaryKeyRelatedField
from .wallet import WalletSafeSerializer


class StatusSafeSerializer(serializers.ModelSerializer):
    wallet = WalletSafeSerializer()

    class Meta:
        model = Status
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        c_exclude = kwargs.pop('c_exclude', [])

        if c_exclude:
            for key in c_exclude:
                self.fields.pop(key, None)

        super().__init__(*args, **kwargs)


class StatusNotSafeSerializer(serializers.ModelSerializer):
    wallet = CurrentPartnerWalletsPrimaryKeyRelatedField()

    class Meta:
        model = Status
        fields = '__all__'

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Status.objects.all(),
                fields=('wallet', 'name',),
                message='Статус карты с таким наименованием уже существует.'
            ),
        )

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

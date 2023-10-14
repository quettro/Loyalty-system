from apps.base.models import ServiceCategory
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ....fields import CurrentPartnerWalletsPrimaryKeyRelatedField
from ..wallet import WalletSafeSerializer


class ServiceCategorySafeSerializer(serializers.ModelSerializer):
    wallet = WalletSafeSerializer()

    class Meta:
        model = ServiceCategory
        fields = '__all__'


class ServiceCategoryNotSafeSerializer(serializers.ModelSerializer):
    wallet = CurrentPartnerWalletsPrimaryKeyRelatedField()

    class Meta:
        model = ServiceCategory
        fields = '__all__'

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=ServiceCategory.objects.all(),
                fields=('wallet', 'name',),
                message='Категория с таким наименованием уже существует.'
            ),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.context['view'].action in ('update', 'partial_update',):
            self.fields.get('wallet').read_only = True

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

from apps.base.models import ProductCategory
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ....fields import CurrentPartnerWalletsPrimaryKeyRelatedField
from ..wallet import WalletSafeSerializer


class ProductCategorySafeSerializer(serializers.ModelSerializer):
    wallet = WalletSafeSerializer()

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductCategoryNotSafeSerializer(serializers.ModelSerializer):
    wallet = CurrentPartnerWalletsPrimaryKeyRelatedField()

    class Meta:
        model = ProductCategory
        fields = '__all__'

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=ProductCategory.objects.all(),
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

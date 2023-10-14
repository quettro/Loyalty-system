from apps.base.models import Product
from rest_framework import serializers

from ....fields import CurrentPartnerProductCategoriesPrimaryKeyRelatedField
from .category import ProductCategorySafeSerializer


class ProductSafeSerializer(serializers.ModelSerializer):
    category = ProductCategorySafeSerializer()

    class Meta:
        model = Product
        fields = '__all__'


class ProductNotSafeSerializer(serializers.ModelSerializer):
    category = CurrentPartnerProductCategoriesPrimaryKeyRelatedField()

    class Meta:
        model = Product
        fields = '__all__'

        extra_kwargs = {
            'is_use_cashback': {'required': True},
            'is_show': {'required': True},
        }

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Product.objects.all(),
                fields=('category', 'name',),
                message='Товар с таким наименованием уже существует.'
            ),
        )

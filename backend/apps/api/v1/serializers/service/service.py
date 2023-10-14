from apps.base.models import Service
from rest_framework import serializers

from ....fields import CurrentPartnerServiceCategoriesPrimaryKeyRelatedField
from .category import ServiceCategorySafeSerializer


class ServiceSafeSerializer(serializers.ModelSerializer):
    category = ServiceCategorySafeSerializer()

    class Meta:
        model = Service
        fields = '__all__'


class ServiceNotSafeSerializer(serializers.ModelSerializer):
    category = CurrentPartnerServiceCategoriesPrimaryKeyRelatedField()

    class Meta:
        model = Service
        fields = '__all__'

        extra_kwargs = {
            'is_show': {'required': True},
            'is_use_cashback': {'required': True},
        }

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Service.objects.all(),
                fields=('category', 'name',),
                message='Услуга с таким наименованием уже существует.'
            ),
        )

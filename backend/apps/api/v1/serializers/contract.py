from apps.documents.models import Contract
from rest_framework import serializers


class ContractSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        exclude = ('id',)

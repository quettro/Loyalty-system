from apps.base.models import PartnerTransaction
from rest_framework import serializers


class PartnerTransactionSafeSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = PartnerTransaction
        exclude = ('partner', 'balance',)

    def get_type(self, obj):
        return obj.get_type_dict()

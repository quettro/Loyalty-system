from apps.base.models import Cert
from django.core.exceptions import ValidationError
from rest_framework import serializers

from ...fields import CurrentPartnerHiddenField


class CertSerializer(serializers.ModelSerializer):
    partner = CurrentPartnerHiddenField()
    p12_cert_pem = serializers.HiddenField(default=None)
    p12_cert_key = serializers.HiddenField(default=None)
    p12_days_left = serializers.SerializerMethodField()

    class Meta:
        model = Cert
        fields = '__all__'

        extra_kwargs = {
            'p12_cert': {'write_only': True},
            'p12_password': {'write_only': True},
            'p12_organization_name': {'read_only': True},
            'p12_team_identifier': {'read_only': True},
            'p12_pass_type_identifier': {'read_only': True},
            'p12_activated_at': {'read_only': True},
            'p12_expires_at': {'read_only': True},
            'p8_cert': {'write_only': True},
            'p8_key': {'write_only': True},
        }

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Cert.objects.all(),
                fields=('partner', 'name',),
                message='Сертификат с таким наименованием уже существует.'
            ),
        )

    def get_p12_days_left(self, obj):
        return obj.p12_days_left

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

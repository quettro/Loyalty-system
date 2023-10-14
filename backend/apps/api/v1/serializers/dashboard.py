from datetime import date

from rest_framework import serializers

from ...fields import CurrentPartnerWalletsPrimaryKeyRelatedField


class DashboardNotSafeSerializer(serializers.Serializer):
    wallet = CurrentPartnerWalletsPrimaryKeyRelatedField(required=False)

    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, attrs):
        if attrs.get('from_date'):
            if not attrs.get('to_date'):
                raise serializers.ValidationError({
                    'to_date': [
                        'Обязательное поле.'
                    ]
                })

            if attrs['from_date'] > date.today():
                raise serializers.ValidationError({
                    'from_date': [
                        ('Дата начала периода не может быть больше '
                         'текущей даты.')
                    ]
                })

            if attrs['from_date'] > attrs['to_date']:
                raise serializers.ValidationError({
                    'from_date': [
                        ('Дата начала периода не может быть больше '
                         'даты его окончания.')
                    ]
                })

        if attrs.get('to_date'):
            if not attrs.get('from_date'):
                raise serializers.ValidationError({
                    'from_date': [
                        'Обязательное поле.'
                    ]
                })

            if attrs['to_date'] > date.today():
                raise serializers.ValidationError({
                    'to_date': [
                        ('Дата окончания периода не может быть больше '
                         'текущей даты.')
                    ]
                })

        return super().validate(attrs)

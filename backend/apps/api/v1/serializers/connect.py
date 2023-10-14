import logging

from apps.base.models import Client, PartnerTransaction, Verification
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from libraries.smsc import SmsC
from rest_framework import serializers

log = logging.getLogger(__name__)


class ConnectNotSafeSerializer(serializers.ModelSerializer):
    token = serializers.SlugRelatedField(
        queryset=Verification.objects.filter(
            status=Verification.Status.CONFIRMED, is_used=False
        ).all(),

        slug_field='token', error_messages={
            'does_not_exist': 'Токен недействителен или отсутствует.'
        }
    )

    class Meta:
        model = Client
        fields = ('name', 'sex', 'brithday', 'token',)

    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def registration(self, wallet):
        token = self.validated_data.pop('token', None)
        token.is_used = True
        token.save()

        instance = wallet.clients.filter(phone=token.phone).first()

        if not instance:
            instance = self.save(
                partner=wallet.partner,
                wallet=wallet,
                status=wallet.statuses.filter(is_by_default=True).first(),
                phone=token.phone
            )
        else:
            if instance.is_deleted:
                instance.deleted_at = None
                instance.save()

        return instance


class ConnectVerificationNotSafeSerializer(serializers.ModelSerializer):
    token = serializers.SlugRelatedField(
        queryset=Verification.objects.filter(
            status=Verification.Status.NOT_CONFIRMED, is_used=False
        ).all(),

        required=False, slug_field='token', error_messages={
            'does_not_exist': 'Токен недействителен или отсутствует.'
        }
    )
    is_verification_code = serializers.BooleanField(required=True)

    class Meta:
        model = Verification
        fields = ('token', 'phone', 'code', 'is_verification_code',)

        extra_kwargs = {
            'phone': {'required': False},
            'code': {'required': False},
        }

    def validate(self, attrs):
        if attrs['is_verification_code']:
            for key in ('code', 'token',):
                if attrs.get(key) is None:
                    raise serializers.ValidationError({
                        key: [
                            'Обязательное поле.'
                        ]
                    })
        else:
            if attrs.get('phone') is None:
                raise serializers.ValidationError({
                    'phone': [
                        'Обязательное поле.'
                    ]
                })
        return super().validate(attrs)

    def verification(self, request, partner):
        if self.validated_data['is_verification_code']:
            return self.__verification_code()
        return self.__verification_phone(request, partner)

    def __verification_code(self):
        phone_verification = self.validated_data['token']

        if phone_verification.code != self.validated_data['code']:
            raise serializers.ValidationError({
                'code': [
                    'Недействительный код.'
                ]
            })

        phone_verification.status = Verification.Status.CONFIRMED
        phone_verification.save()

        return phone_verification

    def __verification_phone(self, request, partner):
        timestamp = request.session.get('verification_phone_timestamp')
        phone = self.validated_data['phone']

        if timestamp:
            self.__validate_timeout(timestamp)

        self.__validate_partner_balance(partner, phone)

        phone_verification = Verification.objects.filter(
            phone=phone,
            status=Verification.Status.NOT_CONFIRMED,
            is_used=False
        ).first()

        if not phone_verification:
            self.validated_data.pop('token', None)
            self.validated_data.pop('code', None)
            self.validated_data.pop('is_verification_code', None)

            phone_verification = self.save(
                partner=partner,
                status=Verification.Status.NOT_CONFIRMED,
                is_used=False
            )
        else:
            self.__validate_timeout(phone_verification.updated_at.timestamp())

        timestamp = timezone.now().timestamp()
        request.session['verification_phone_timestamp'] = timestamp

        message = (
            'Отправка запроса на выполнение звонка. '
            'Номер телефона: {}. Дополнительные данные: {}'
        )

        log.info(
            message.format(
                phone,
                phone_verification.__dict__
            )
        )

        response = self.__call(phone_verification.phone)

        message = (
            'Звонок на номер телефона: {}, успешно был отправлен. '
            'Полученные данные: {}. Дополнительные данные: {}'
        )

        log.info(
            message.format(
                phone,
                response,
                phone_verification.__dict__
            )
        )

        phone_verification.smsc_id = response['id']
        phone_verification.code = response['code'][2:]
        phone_verification.save()

        return phone_verification

    def __validate_timeout(self, timestamp):
        difference = timezone.now().timestamp() - timestamp
        timeout = settings.PHONE_VERIFICATION_TIMEOUT.total_seconds()
        sec = round((timeout - difference), 0)

        if sec > 0:
            raise serializers.ValidationError({
                'phone': [
                    f'Повторите текущее действие через {sec} сек.'
                ]
            })

    def __validate_partner_balance(self, partner, phone):
        count = partner.tariff.count_verifications_included_in_the_price
        cost = partner.tariff.cost_of_verification_by_call / count

        if not partner.is_it_possible_deduct_from_balance(cost):
            raise serializers.ValidationError({
                'phone': [
                    'В данный момент, верификация номера недоступна.'
                ]
            })

        partner.transactions.create(
            type=PartnerTransaction.Type.DEBIT,
            amount=cost,
            message=(
                'Списание средств за верификацию номера телефона: '
                f'{phone[:-4]}****.'
            )
        )

    def __call(self, phone):
        smsc = SmsC()
        smsc.set_phone(phone)

        try:
            response = smsc.call()
        except Exception as e:
            log.error(e, exc_info=True)

            raise serializers.ValidationError({
                'phone': [
                    'Что-то пошло не так... Повторите попытку чуть позже.'
                ]
            })

        return response  # noqa

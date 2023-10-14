from datetime import date
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_json_field_schema_validator.validators import \
    JSONFieldSchemaValidator

from ..choices import ChoiceDict
from ..fields import LimitedImageField
from ..managers import WalletManager
from ..regex import REGEX
from ..schema import WALLET
from .cert import Cert
from .partner import Partner

from django.core.validators import (  # isort: skip
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
    FileExtensionValidator
)


class Wallet(models.Model):
    class Type(ChoiceDict, models.TextChoices):
        DISCOUNT = 'DISCOUNT', 'Скидочная карта'
        BONUS = 'BONUS', 'Бонусная карта'
        CHOP = 'CHOP', 'Чоп-карта'

    DISCOUNT_FIELDS = (
        'discount',
    )

    BONUS_FIELDS = (
        'cashback',
        'conversion',
        'is_use_welcome_bonuses',
        'bonuses',
        'is_immediately_transfer_bonuses',
        'min_expenditure_obtaining_bonuses',
        'is_burn_bonuses',
        'validity_period_of_bonuses',
    )

    CHOP_FIELDS = (
        'stamps',
        'is_unlimited',
        'is_message_about_bonus_received_displayed',
        'active_stamp_icon',
        'nonactive_stamp_icon',
        'finish_stamp_icon',
    )

    """
    Основная информация
    """
    partner = models.ForeignKey(
        Partner,
        verbose_name='Партнер',
        on_delete=models.PROTECT,
        related_name='wallets'
    )
    cert = models.ForeignKey(
        Cert,
        verbose_name='Сертификат IOS',
        on_delete=models.PROTECT,
        related_name='wallets'
    )
    uuid = models.UUIDField(
        verbose_name='UUID',
        default=uuid4,
        editable=False,
        unique=True
    )
    name = models.CharField(
        verbose_name='Название карты',
        max_length=255
    )
    snumbers = models.CharField(
        verbose_name='Стартовый номер карты',
        max_length=10,
        validators=(RegexValidator(**REGEX['SNUMBERS']),),
    )
    type = models.CharField(
        verbose_name='Тип создаваемой карты',
        max_length=20,
        choices=Type.choices
    )

    """
    Скидочная карта
    """
    discount = models.PositiveSmallIntegerField(
        verbose_name='Базовая скидка',
        default=0,
        validators=(MinValueValidator(0), MaxValueValidator(100),),
        help_text=(
            'Минимальная скидка: 0%, Максимальная скидка: 100%. '
            'Необходимо указывать, если тип карты: Скидочная карта'
        )
    )

    """
    Бонусная карта
    """
    cashback = models.PositiveSmallIntegerField(
        verbose_name='Базовый кэшбэк',
        default=0,
        validators=(MinValueValidator(0), MaxValueValidator(100),),
        help_text=(
            'Минимальный кэшбэк: 0%, Максимальный кэшбэк: 100%. '
            'Необходимо указывать, если тип карты: Бонусная карта'
        )
    )
    conversion = models.PositiveSmallIntegerField(
        verbose_name='Конверсия баллов',
        default=1,
        validators=(MinValueValidator(1), MaxValueValidator(30000),),
        help_text=(
            'Скольким баллам равен один рубль. '
            'Необходимо указывать, если тип карты: Бонусная карта'
        )
    )
    is_use_welcome_bonuses = models.BooleanField(
        verbose_name='Начислять приветственные баллы?',
        default=False,
        help_text='Необходимо указывать, если тип карты: Бонусная карта'
    )
    bonuses = models.DecimalField(
        verbose_name='Количество начисляемых баллов',
        default=0,
        max_digits=12,
        decimal_places=2,
        help_text='Необходимо указывать, если тип карты: Бонусная карта'
    )
    is_immediately_transfer_bonuses = models.BooleanField(
        verbose_name='Начислить приветственные баллы сразу?',
        default=False,
        help_text='Необходимо указывать, если тип карты: Бонусная карта'
    )
    min_expenditure_obtaining_bonuses = models.DecimalField(
        verbose_name='Сумма расходов для начисления',
        default=0,
        max_digits=12,
        decimal_places=2,
        help_text='Необходимо указывать, если тип карты: Бонусная карта'
    )
    is_burn_bonuses = models.BooleanField(
        verbose_name='Использовать сгорание баллов?',
        default=False,
        help_text='Необходимо указывать, если тип карты: Бонусная карта'
    )
    validity_period_of_bonuses = models.PositiveSmallIntegerField(
        verbose_name='Количество дней после которых баллы сгорают',
        default=1,
        validators=(MinValueValidator(1), MaxValueValidator(30000),),
        help_text='Необходимо указывать, если тип карты: Бонусная карта'
    )

    """
    Чоп карта
    """
    stamps = models.PositiveSmallIntegerField(
        verbose_name='Кол-во штампов',
        default=1,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(settings.MAX_STAMPS),
        )
    )
    is_unlimited = models.BooleanField(
        verbose_name='Безлимитная ли акция?',
        default=False
    )
    is_message_about_bonus_received_displayed = models.BooleanField(
        verbose_name='Отображается ли сообщение о полученном бонусе?',
        default=False
    )
    active_stamp_icon = LimitedImageField(
        verbose_name='Активная иконка штампа',
        upload_to='wallets/stamps/active/%Y/%m/%d/',
        null=True,
        blank=True,
        max_upload_size=1024,
        min_dim=(180, 180),
        max_dim=(180, 180),
        square=True,
        validators=(FileExtensionValidator(['png']),),
        help_text=(
            'Разрешение иконки должен составлять 180 x 180 пикселей. '
            'Допустимые форматы файла: .png. '
            'Максимальный размер одного файла не более 1 Мб.'
        )
    )
    nonactive_stamp_icon = LimitedImageField(
        verbose_name='Не активная иконка штампа',
        upload_to='wallets/stamps/nonactive/%Y/%m/%d/',
        null=True,
        blank=True,
        max_upload_size=1024,
        min_dim=(180, 180),
        max_dim=(180, 180),
        square=True,
        validators=(FileExtensionValidator(['png']),),
        help_text=(
            'Разрешение иконки должен составлять 180 x 180 пикселей. '
            'Допустимые форматы файла: .png. '
            'Максимальный размер одного файла не более 1 Мб. '
            'Если оставить данное поле пустым, то `Активная иконка штампа` '
            'автоматически будет затемнена.'
        )
    )
    finish_stamp_icon = LimitedImageField(
        verbose_name='Финишная иконка штампа',
        upload_to='wallets/stamps/finish/%Y/%m/%d/',
        null=True,
        blank=True,
        max_upload_size=1024,
        min_dim=(180, 180),
        max_dim=(180, 180),
        square=True,
        validators=(FileExtensionValidator(['png']),),
        help_text=(
            'Разрешение иконки должен составлять 180 x 180 пикселей. '
            'Допустимые форматы файла: .png. '
            'Максимальный размер одного файла не более 1 Мб. '
            'Если оставить данное поле пустым, то будет использовано '
            '`Активная иконка штампа` или `Не активная иконка штампа`.'
        )
    )

    """
    Геолокация
    """
    is_use_push_for_geolocation = models.BooleanField(
        verbose_name='Отправлять уведомления пользователям по геолокации?',
        default=False
    )
    geolocations = models.JSONField(
        verbose_name='Данные геолокации в JSON формате',
        null=True,
        blank=True,
        validators=(JSONFieldSchemaValidator(WALLET['GEOLOCATIONS']),),
        help_text=(
            'Необходимо указывать, если включены уведомления '
            'пользователям по геолокации. Правильный пример: '
            '[{"longitude": 0, "latitude": 0, "message": "Добро пожаловать!"}]'
        )
    )

    """
    Изображения
    """
    icon = LimitedImageField(
        verbose_name='Иконка',
        upload_to='wallets/icons/%Y/%m/%d/',
        max_upload_size=1024,
        min_dim=(87, 87),
        square=True,
        validators=(FileExtensionValidator(['png']),),
        help_text=(
            'Минимальный размер файла 87 х 87 пикселя. '
            'Допустимые форматы файла: .png. '
            'Максимальный размер одного файла не более 1 Мб.'
        )
    )
    logotype = LimitedImageField(
        verbose_name='Логотип',
        upload_to='wallets/logotypes/%Y/%m/%d/',
        max_upload_size=1024,
        max_dim=(480, 150),
        validators=(FileExtensionValidator(['png']),),
        help_text=(
            'Максимальный размер файла 480 х 150 пикселя. '
            'Допустимые форматы файла: png. '
            'Максимальный размер одного файла не более 1 Мб.'
        )
    )
    background_image = LimitedImageField(
        verbose_name='Фоновое изображение',
        upload_to='wallets/backgrounds/%Y/%m/%d/',
        max_upload_size=1024,
        min_dim=(1125, 432),
        max_dim=(1125, 432),
        validators=(FileExtensionValidator(['jpg', 'jpeg']),),
        help_text=(
            'Минимальный и максимальный размер файла 1125 х 432 пикселя. '
            'Допустимые форматы файла: jpg, jpeg. '
            'Максимальный размер одного файла не более 1 Мб.'
        )
    )

    """
    Внешний вид карты
    """
    frontend = models.JSONField(
        verbose_name='Передняя часть карты',
        validators=(JSONFieldSchemaValidator(WALLET['FRONTEND']),)
    )
    backend = models.JSONField(
        verbose_name='Задняя часть карты',
        validators=(JSONFieldSchemaValidator(WALLET['BACKEND']),)
    )

    """
    Важные даты
    """
    expires_at = models.DateField(
        verbose_name='Срок действия карты до',
        null=True,
        blank=True
    )
    deleted_at = models.DateTimeField(
        verbose_name='Дата удаления карты (Мягкое удаление)',
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата последнего обновления',
        auto_now=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    objects = WalletManager()

    class Meta:
        verbose_name = 'Карта'
        verbose_name_plural = 'Карты'
        ordering = ('-id',)

        constraints = (
            models.UniqueConstraint(
                fields=('partner', 'name'),
                name='unique_wallet_by_partner'
            ),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._stamps = self.stamps
        self._expires_at = self.expires_at

    def __str__(self):
        return 'Name: {} | Type: {} | Deleted at: {}' . format(
            self.name, self.get_type().label, self.deleted_at)

    def clean(self):
        if hasattr(self, 'partner'):
            if not self.id and self.partner.is_max_templates:
                raise ValidationError({
                    'partner': [
                        'Достигнут лимит по создаю шаблонов для карт.'
                    ]
                })

            tariff = self.partner.tariff

            if not tariff.is_use_push_for_geolocation:
                if self.is_use_push_for_geolocation:
                    raise ValidationError({
                        'is_use_push_for_geolocation': [
                            ('Данная функция недоступна, '
                                'т.к ограничена тарифом.')
                        ]
                    })
                else:
                    self.geolocations = None
            else:
                if self.is_use_push_for_geolocation:
                    if not self.geolocations:
                        raise ValidationError({
                            'geolocations': [
                                'Обязательное поле.'
                            ]
                        })
                else:
                    self.geolocations = None

        if self.is_type_chop:
            if not self.active_stamp_icon:
                raise ValidationError({
                    'active_stamp_icon': [
                        'Обязательное поле.'
                    ]
                })

            if not self.expires_at:
                raise ValidationError({
                    'expires_at': [
                        'Обязательное поле.'
                    ]
                })

            if self.expires_at != self._expires_at:
                if self.expires_at <= date.today():
                    raise ValidationError({
                        'expires_at': [
                            'Указанная дата не может быть меньше текущей даты.'
                        ]
                    })

            if self.id:
                if self.expires_at != self._expires_at:
                    if self._expires_at > self.expires_at:
                        raise ValidationError({
                            'expires_at': [
                                ('Указанная дата не может быть меньше даты '
                                    f'{self._expires_at}.')
                            ]
                        })

                if self._expires_at > date.today():
                    if self.stamps != self._stamps:
                        raise ValidationError({
                            'stamps': [
                                ('Кол-во штампов нельзя менять, пока акция не '
                                    'завершена.')
                            ]
                        })

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= date.today()

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    @property
    def is_type_discount(self):
        return self.type == self.Type.DISCOUNT

    @property
    def is_type_bonus(self):
        return self.type == self.Type.BONUS

    @property
    def is_type_chop(self):
        return self.type == self.Type.CHOP

    def get_type(self):
        return self.Type(self.type)

    def get_type_dict(self):
        return self.get_type().dict()

    def softdelete(self, is_save=True):
        self.deleted_at = timezone.now()

        if is_save:
            self.save()

    def restore(self, is_save=True):
        self.deleted_at = None

        if is_save:
            self.save()

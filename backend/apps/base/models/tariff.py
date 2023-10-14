from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from ..regex import REGEX
from .permission import Permission


class Tariff(models.Model):
    partner = models.ForeignKey(
        'base.Partner',
        verbose_name='Партнер',
        on_delete=models.PROTECT,
        related_name='tariffs',
        null=True,
        blank=True
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='Доступы к разделам',
        related_name='tariffs'
    )
    max_clients = models.PositiveIntegerField(
        verbose_name='Макс. кол-во клиентов',
        default=0,
        validators=(MinValueValidator(0),)
    )
    cost_additional_client = models.DecimalField(
        verbose_name='Стоимость дополнительного клиента',
        default=0,
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    max_templates = models.PositiveIntegerField(
        verbose_name='Макс. кол-во шаблонов карт',
        default=0,
        validators=(MinValueValidator(0),)
    )
    is_use_push_for_geolocation = models.BooleanField(
        verbose_name='Используются ли PUSH уведомления по геолокации?',
        default=False
    )
    push_limits = models.CharField(
        verbose_name='Лимиты PUSH',
        default='0;0;0',
        max_length=24,
        validators=(RegexValidator(**REGEX['PUSH_NOTIFICATIONS_LIMITS']),),
        help_text='Лимиты PUSH, необходимо вводить в формате: Час;День;Месяц'
    )
    is_use_api = models.BooleanField(
        verbose_name='Используется ли API?',
        default=False
    )
    api_requests_limits = models.CharField(
        verbose_name='Лимиты API',
        default='0;0',
        max_length=16,
        validators=(RegexValidator(**REGEX['API_REQUESTS_LIMIT']),),
        help_text='Лимиты API, необходимо вводить в формате: Час;День'
    )
    is_use_sms = models.BooleanField(
        verbose_name='Используются ли SMS сообщения?',
        default=False
    )
    is_use_sending_cards_by_sms = models.BooleanField(
        verbose_name='СМС отправка карт',
        default=False
    )
    cost_sms_message = models.DecimalField(
        verbose_name='Стоимость SMS сообщения',
        default=0,
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    cost_of_verification_by_call = models.DecimalField(
        verbose_name='Стоимость верификации звонком',
        default=0,
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    count_verifications_included_in_the_price = models.PositiveIntegerField(
        verbose_name='Кол-во верификаций включенных в стоимость',
        default=1,
        validators=(MinValueValidator(1),)
    )
    is_personal_manager = models.BooleanField(
        verbose_name='Личный менеджер',
        default=False
    )
    is_importing_client_database = models.BooleanField(
        verbose_name='Разрешить импорт клиентской базы?',
        default=False
    )
    is_white_label = models.BooleanField(
        verbose_name='While label',
        default=False
    )
    payment = models.DecimalField(
        verbose_name='Ежемесячная/Ежедневная оплата',
        default=0,
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    discounts = models.CharField(
        verbose_name='Скидки на оплату',
        default='0;0;0',
        max_length=12,
        validators=(RegexValidator(**REGEX['DISCOUNTS']),),
        help_text=(
            'Скидки на оплату, необходимо вводить в формате: '
            '3 месяца;6 месяцев;Год'
        )
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата последнего обновления',
        auto_now=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        ordering = ('-id',)

    def __str__(self):
        name = self.name

        if self.is_individual:
            name += f'. [ Партнер: {self.partner} ]'

        return name

    def clean(self):
        discounts = list(map(int, self.discounts.split(';')))

        if min(discounts) < 0 or max(discounts) > 100:
            raise ValidationError({
                'discounts': [
                    ('Скидки на оплату, необходимо указывать в диапазоне '
                     'от 0 до 100.')
                ]
            })

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_individual(self):
        """
        Проверяем, индивидуальный ли тариф. Если поле `partner` заполнено,
        значит тариф индивидуальный.

        Пример:
        tariff = Tariff.objects.get()
        tariff->is_individual
        """
        return self.partner is not None

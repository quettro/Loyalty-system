from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from ...choices import ChoiceDict
from ..company import Company
from ..tariff import Tariff
from .type import PartnerType


class Partner(models.Model):
    class SubscriptionFee(ChoiceDict, models.TextChoices):
        DAILY = 'DAILY', 'Ежедневно равными частями'
        MONTHLY = 'MONTHLY', 'Ежемесячно'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.PROTECT
    )
    type = models.ForeignKey(
        PartnerType,
        verbose_name='Тип партнера',
        on_delete=models.PROTECT,
        related_name='partners'
    )
    company = models.OneToOneField(
        Company,
        verbose_name='Компания',
        on_delete=models.PROTECT
    )
    place_name = models.CharField(
        verbose_name='Наименование заведения',
        max_length=255
    )
    address = models.CharField(
        verbose_name='Адрес заведения',
        max_length=255
    )
    balance = models.DecimalField(
        verbose_name='Баланс',
        default=0,
        max_digits=12,
        decimal_places=2
    )
    locations = models.PositiveIntegerField(
        verbose_name='Кол-во точек',
        default=0,
        validators=(MinValueValidator(0),)
    )
    tariff = models.ForeignKey(
        Tariff,
        verbose_name='Тариф',
        on_delete=models.PROTECT,
        related_name='partners'
    )
    is_show_client_phones = models.BooleanField(
        verbose_name='Партнер может видеть номера телефонов клиентов?',
        default=False
    )
    is_negative_balance = models.BooleanField(
        verbose_name='Разрешить отрицательный баланс?',
        default=False
    )
    limit_negative_balance = models.DecimalField(
        verbose_name='Лимит отрицательного баланса',
        default=0,
        max_digits=12,
        decimal_places=2
    )
    debiting_subscription_fee = models.CharField(
        verbose_name='Списание абон. платы',
        max_length=30,
        choices=SubscriptionFee.choices
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
        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнеры'
        ordering = ('-id',)

    def __str__(self):
        return self.user.get_full_name()

    def clean(self):
        if hasattr(self, 'user'):
            if self.user.is_employee:
                raise ValidationError({
                    'user': [
                        (f'Сотрудника `{self.user.get_full_name()}` нельзя '
                            'назначить как партнера.')
                    ]
                })
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_contract(self):
        """ Принял ли партнер договор. """
        return hasattr(self, 'contract') and self.contract is not None

    @property
    def is_max_clients(self):
        """ Достигнут ли лимит клиентов. """
        return self.clients.count() >= self.tariff.max_clients

    @property
    def is_max_templates(self):
        """ Достигнут ли лимит шаблонов карт. """
        return self.wallets.not_deleted().count() >= self.tariff.max_templates

    def is_it_possible_deduct_from_balance(self, amount):
        """ Можно ли вычесть определенную сумму с баланса? """
        limit = self.limit_negative_balance if self.is_negative_balance else 0
        return (self.balance - amount) >= limit

    def update_tariff_partner(self, instance=None):
        self.tariff.partner = instance
        self.tariff.save()

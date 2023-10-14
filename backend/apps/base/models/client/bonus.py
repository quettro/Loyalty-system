import datetime
import logging

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from ...choices import ChoiceDict
from ..wallet import Wallet

log = logging.getLogger(__name__)


class Bonus(models.Model):
    """
    Данная модель отвечает за транзакцию баллов клиента. Клиент может получить
    баллы только в том случае, если у него тип карты: Бонусная карта.
    """

    class Type(ChoiceDict, models.TextChoices):
        CREDIT = 'CREDIT', 'Зачисление'
        DEBIT = 'DEBIT', 'Списание'

    client = models.ForeignKey(
        'base.Client',
        verbose_name='Клиент',
        on_delete=models.PROTECT,
        related_name='t_bonuses'
    )
    transaction = models.ForeignKey(
        'base.ClientTransaction',
        verbose_name='Транзакция клиента',
        on_delete=models.PROTECT,
        related_name='t_transactions',
        null=True,
        blank=True,
        help_text=(
            'Если выбрана транзакция клиента, а так-же выбран тип операции: '
            f'{Type.DEBIT.label}, то клиенту будут начислены баллы.'
        )
    )
    type = models.CharField(
        verbose_name='Тип операции',
        max_length=20,
        choices=Type.choices
    )
    count = models.DecimalField(
        verbose_name='Кол-во баллов для зачисления/списания',
        default=0,
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    message = models.TextField(
        verbose_name='Примечание',
        max_length=2048,
        null=True,
        blank=True
    )
    is_burned_bonuses = models.BooleanField(
        verbose_name='Сгорели ли бонусы?',
        default=False
    )
    expires_at = models.DateField(
        verbose_name='Срок действия баллов до',
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

    class Meta:
        verbose_name = 'Транзакция баллов'
        verbose_name_plural = 'Транзакции баллов'
        ordering = ('-id',)

    def __init__(self, *args, **kwargs):
        self.is_auto_update_client = kwargs.pop('is_auto_update_client', True)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'{self.client.name} | {self.count}'

    def clean(self):
        if self.message is not None and len(self.message) <= 0:
            self.message = None

        if hasattr(self, 'client') and self.client is not None:
            if not self.client.wallet.is_type_bonus:
                raise ValidationError({
                    'client': [
                        ('Тип карты клиента не соответствует типу: '
                            f'{Wallet.Type.BONUS.label}')
                    ]
                })

            if self.is_type_debit and (self.client.balance - self.count) < 0:
                raise ValidationError({
                    'count': [
                        ('Кол-во баллов для списания превышает '
                            f'допустимый лимит в {self.client.balance} б.')
                    ]
                })

            if hasattr(self, 'transaction') and self.transaction is not None:
                if self.client.id != self.transaction.client.id:
                    raise ValidationError({
                        'transaction': [
                            ('Данная транзакция не относится к '
                                'выбранному клиенту.')
                        ]
                    })

        if self.is_type_debit and self.is_burned_bonuses:
            raise ValidationError({
                'is_burned_bonuses': [
                    ('Тип операции не соответствует типу: '
                        f'{self.Type.CREDIT.label}')
                ]
            })

        if self.expires_at and self.expires_at <= datetime.date.today():
            raise ValidationError({
                'expires_at': [
                    'Указанная дата не может быть меньше текущей даты.'
                ]
            })

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.expires_at:
            if self.client.wallet.is_burn_bonuses:
                self.expires_at = timezone.now() + datetime.timedelta(
                    days=self.client.wallet.validity_period_of_bonuses)

        return super().save(*args, **kwargs)

    @property
    def is_type_credit(self):
        return self.type == self.Type.CREDIT

    @property
    def is_type_debit(self):
        return self.type == self.Type.DEBIT

    def get_type(self):
        return self.Type(self.type)

    def get_type_dict(self):
        return self.get_type().dict()

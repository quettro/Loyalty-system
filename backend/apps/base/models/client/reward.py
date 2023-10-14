from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ...choices import ChoiceDict
from ..wallet import Wallet


class Reward(models.Model):
    """
    Данная модель отвечает за транзакцию наград клиента. Клиент может получить
    награду только в том случае, если у него тип карты: Чоп-карта.
    """

    class Type(ChoiceDict, models.TextChoices):
        CREDIT = 'CREDIT', 'Зачисление'
        DEBIT = 'DEBIT', 'Списание'

    client = models.ForeignKey(
        'base.Client',
        verbose_name='Клиент',
        on_delete=models.PROTECT,
        related_name='t_rewards'
    )
    type = models.CharField(
        verbose_name='Тип операции',
        max_length=20,
        choices=Type.choices
    )
    count = models.PositiveSmallIntegerField(
        verbose_name='Кол-во наград для зачисления/списания',
        default=1,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(settings.MAX_REWARDS),
        )
    )
    message = models.TextField(
        verbose_name='Примечание',
        max_length=2048,
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
        verbose_name = 'Транзакция наград'
        verbose_name_plural = 'Транзакции наград'
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
            if not self.client.wallet.is_type_chop:
                raise ValidationError({
                    'client': [
                        ('Тип карты клиента не соответствует типу: '
                            f'{Wallet.Type.CHOP.label}')
                    ]
                })

            if self.is_type_credit:
                if (self.count + self.client.a_rewards) > settings.MAX_REWARDS:
                    v = settings.MAX_REWARDS - self.client.a_rewards

                    raise ValidationError({
                        'count': [
                            ('Кол-во наград для зачисления превышает '
                                f'допустимый лимит в {v} н.')
                        ]
                    })

            elif self.is_type_debit:
                if (self.client.a_rewards - self.count) < 0:
                    v = self.client.a_rewards

                    raise ValidationError({
                        'count': [
                            ('Кол-во наград для списания превышает '
                                f'допустимый лимит в {v} н.')
                        ]
                    })

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
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

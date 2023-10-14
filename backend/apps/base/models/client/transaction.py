from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..wallet import Wallet


class ClientTransaction(models.Model):
    client = models.ForeignKey(
        'base.Client',
        verbose_name='Клиент',
        on_delete=models.PROTECT,
        related_name='transactions',
    )
    receipt = models.PositiveIntegerField(
        verbose_name='Номер чека',
        null=True,
        blank=True,
        validators=(MinValueValidator(0), MaxValueValidator(2147000000),)
    )
    amount = models.DecimalField(
        verbose_name='Стоимость покупки',
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    percent = models.PositiveSmallIntegerField(
        verbose_name='% Кэшбэка/Скидки',
        null=True,
        blank=True,
        validators=(MinValueValidator(0), MaxValueValidator(100),),
        help_text=(
            'Минимальный процент: 0%, Максимальный процент: 100%. '
            'Если оставить данное поле пустым, то значение будет рассчитано '
            'автоматически.'
        )
    )
    message = models.TextField(
        verbose_name='Примечание',
        max_length=2048,
        null=True,
        blank=True
    )
    is_auto_add_bonuses = models.BooleanField(
        verbose_name='Зачислить баллы автоматически?',
        default=False
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
        verbose_name = 'Транзакция клиента'
        verbose_name_plural = 'Транзакции клиентов'
        ordering = ('-id',)

    def __str__(self):
        return f'Client: {self.client.name} | Amount: {self.amount}'

    def clean(self):
        if self.message is not None and len(self.message) <= 0:
            self.message = None

        if hasattr(self, 'client') and self.client is not None:
            if self.percent is not None:
                if self.client.wallet.is_type_chop:
                    raise ValidationError({
                        'percent': [
                            ('Тип карты клиента не соответствует типу: '
                                f'`{Wallet.Type.DISCOUNT.label}` или '
                                f'`{Wallet.Type.BONUS.label}`')
                        ]
                    })
            else:
                if self.client.wallet.is_type_discount:
                    self.percent = self.client.discount

                elif self.client.wallet.is_type_bonus:
                    self.percent = self.client.cashback

            if self.is_auto_add_bonuses:
                if not self.client.wallet.is_type_bonus:
                    raise ValidationError({
                        'is_auto_add_bonuses': [
                            ('Тип карты клиента не соответствует типу: '
                                f'{Wallet.Type.BONUS.label}')
                        ]
                    })

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

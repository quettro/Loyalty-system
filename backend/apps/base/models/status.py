from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..validators import check_if_the_wallet_has_been_deleted
from .wallet import Wallet


class Status(models.Model):
    """
    Модель отвечает за статусы карт (Дополнительные скидки за выполненные
    условия). В зависимости от суммы покупок/кол-во визитов и тд. клиенту
    присваевается статус с дополнительными скидками. У каждой карты
    обязательно должен быть один статус по умолчанию.
    """
    wallet = models.ForeignKey(
        Wallet,
        verbose_name='Карта партнера',
        on_delete=models.PROTECT,
        related_name='statuses'
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
    )
    percent = models.PositiveSmallIntegerField(
        verbose_name='% Кэшбэка/Скидки',
        validators=(MinValueValidator(0), MaxValueValidator(100),),
        help_text='Минимальный процент: 0%, Максимальный процент: 100%.'
    )
    expenses = models.DecimalField(
        verbose_name='Сумма покупок',
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    visits = models.PositiveSmallIntegerField(
        verbose_name='Кол-во визитов',
        validators=(MinValueValidator(0), MaxValueValidator(30000),)
    )
    number_of_days_with_us = models.PositiveSmallIntegerField(
        verbose_name='Кол-во дней с момента регистрации',
        validators=(MinValueValidator(0), MaxValueValidator(30000),)
    )
    is_by_default = models.BooleanField(
        verbose_name='По умолчанию',
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
        verbose_name = 'Статус карты'
        verbose_name_plural = 'Статусы карт'
        ordering = ('-id',)

        constraints = (
            models.UniqueConstraint(
                fields=('wallet', 'name'),
                name='unique_status_by_wallet'
            ),
        )

    def __str__(self):
        return self.name

    def clean(self):
        if hasattr(self, 'wallet') and self.wallet is not None:
            if not self.id:
                check_if_the_wallet_has_been_deleted(self.wallet)

            if self.is_by_default:
                objects = self.wallet.statuses.filter(is_by_default=True)
                objects = objects.exclude(id=self.id) if self.id else objects

                if objects.exists():
                    raise ValidationError({
                        'is_by_default': [
                            'У данной карты уже есть статус по умолчанию.'
                        ]
                    })

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

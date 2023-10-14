import logging

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from ...choices import ChoiceDict

log = logging.getLogger(__name__)


class PartnerTransaction(models.Model):
    class Type(ChoiceDict, models.TextChoices):
        CREDIT = 'CREDIT', 'Зачисление средств'
        DEBIT = 'DEBIT', 'Списание средств'

    partner = models.ForeignKey(
        'base.Partner',
        verbose_name='Партнер',
        on_delete=models.PROTECT,
        related_name='transactions',
    )
    type = models.CharField(
        verbose_name='Тип операции',
        max_length=20,
        choices=Type.choices
    )
    amount = models.DecimalField(
        verbose_name='Сумма для зачисления/списания',
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    balance = models.DecimalField(
        verbose_name='Баланс',
        max_digits=12,
        decimal_places=2,
        editable=False
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
        verbose_name = 'Транзакция партнера'
        verbose_name_plural = 'Транзакции партнеров'
        ordering = ('-id',)

    def __str__(self):
        return self.partner.user.get_full_name()

    def clean(self):
        if not self.id:
            if hasattr(self, 'partner') and self.is_type_debit:
                partner = self.partner

                if not partner.is_it_possible_deduct_from_balance(self.amount):
                    raise ValidationError({
                        'amount': [
                            ('Данную сумму невозможно списать со '
                                'счета партнера.')
                        ]
                    })

        if self.message is not None and len(self.message) <= 0:
            self.message = None

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.id:
            """
            Если транзакция не создана, то начисляем/списываем партнеру
            определенную сумму. Начисляем/списываем именно в методе
            `save`, а не в `clean`, т.к метод `clean` может сработать 2 раза
            и соотвественно баланс партнера обновиться 2 раза, а это плохо.
            """
            amount = self.amount

            if self.is_type_debit:
                amount = -amount

            self.partner.balance += amount
            self.partner.save()
            self.balance = self.partner.balance

            log.info((
                '[ {} ] Создана транзакция партнера на сумму: {}. '
                'Примечание: {} - [ Дополнительные данные: {} ]'
            ).format(
                self.get_type().label, self.amount,
                self.message, self.__dict__
            ))

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

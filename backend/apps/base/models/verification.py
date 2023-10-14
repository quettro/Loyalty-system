import logging
import uuid

from django.core.validators import RegexValidator
from django.db import models

from ..choices import ChoiceDict
from ..regex import REGEX
from .partner import Partner

log = logging.getLogger(__name__)


class Verification(models.Model):
    class Status(ChoiceDict, models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Подтверждён'
        NOT_CONFIRMED = 'NOT_CONFIRMED', 'Не подтверждён'

    partner = models.ForeignKey(
        Partner,
        verbose_name='Партнер',
        on_delete=models.PROTECT,
        related_name='verifications'
    )
    token = models.UUIDField(
        verbose_name='Токен',
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    phone = models.CharField(
        verbose_name='Номер телефона',
        max_length=12,
        validators=(RegexValidator(**REGEX['PHONE']),)
    )
    smsc_id = models.PositiveIntegerField(
        verbose_name='Идентификатор сообщения в сервисе smsc.ru',
        default=0
    )
    code = models.CharField(
        verbose_name='Код',
        max_length=5,
        validators=(RegexValidator(**REGEX['CODE']),)
    )
    status = models.CharField(
        verbose_name='Статус',
        max_length=20,
        choices=Status.choices
    )
    is_used = models.BooleanField(
        verbose_name='Использован ли номер телефона?',
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
        verbose_name = 'Верификация'
        verbose_name_plural = 'Верификации'
        ordering = ('-id',)

    def __str__(self):
        return self.phone

    def save(self, *args, **kwargs):
        if self.is_status_confirmed:
            log.info((
                'Номер телефона: {}, успешно был подтвержден. Код: {}. '
                'Дополнительные данные: {}'
            ).format(self.phone, self.code, self.__dict__))

        return super().save(*args, **kwargs)

    @property
    def is_status_confirmed(self):
        return self.status == self.Status.CONFIRMED

    @property
    def is_status_not_confirmed(self):
        return self.status == self.Status.NOT_CONFIRMED

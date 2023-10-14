from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ..choices import ChoiceDict
from ..validators import check_if_the_wallet_has_been_deleted
from .audience import Audience
from .wallet import Wallet


class Push(models.Model):
    """
    Отправка/Планирование/История пуш уведомлений. Сигналы: signals -> push.py
    """

    class Status(ChoiceDict, models.TextChoices):
        WAITING = 'WAITING', 'Ожидание'
        PROCESSING = 'PROCESSING', 'В обработке'
        COMPLETED = 'COMPLETED', 'Завершено'

    wallet = models.ForeignKey(
        Wallet,
        verbose_name='Карта партнера',
        on_delete=models.PROTECT,
        related_name='push'
    )
    audience = models.ForeignKey(
        Audience,
        verbose_name='Аудитория',
        on_delete=models.PROTECT,
        related_name='push',
        null=True,
        blank=True,
        help_text=(
            'Если оставить данное поле пустым, то пуш уведомления будут '
            'отправлены всем активным клиентам выбранной карты.'
        )
    )
    task_id = models.UUIDField(
        verbose_name='Идентификатор задачи',
        editable=False,
        null=True,
        blank=True
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
    )
    message = models.TextField(
        verbose_name='Текст рассылки',
        max_length=2048
    )
    status = models.CharField(
        verbose_name='Статус',
        max_length=20,
        default=Status.WAITING,
        choices=Status.choices
    )
    is_send_immediately = models.BooleanField(
        verbose_name='Отправить немедленно?',
        default=False
    )
    send_at = models.DateTimeField(
        verbose_name='Дата и время отправки',
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
        verbose_name = 'Пуш уведомление'
        verbose_name_plural = 'Пуш уведомления'
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def clean(self):
        if hasattr(self, 'wallet') and self.wallet is not None:
            if hasattr(self, 'audience') and self.audience is not None:
                if self.wallet.id != self.audience.wallet.id:
                    raise ValidationError({
                        'audience': [
                            ('Данная фильтрация не принадлежит '
                                'выбранной карте.')
                        ]
                    })

        if not self.id:
            if hasattr(self, 'wallet') and self.wallet is not None:
                check_if_the_wallet_has_been_deleted(self.wallet)

                push_limits = self.wallet.partner.tariff.push_limits
                push_limits = list(map(int, push_limits.split(';')))

                filter = {'wallet__partner__id': self.wallet.partner.id}

                counts = Push.objects.filter(**filter).aggregate(
                    hour=models.Count(models.Q(
                        created_at__gte=(
                            timezone.now() - timezone.timedelta(
                                hours=1
                            )
                        )
                    )),
                    day=models.Count(models.Q(
                        created_at__gte=(
                            timezone.now().replace(
                                hour=0,
                                minute=0,
                                second=0,
                                microsecond=0
                            )
                        )
                    )),
                    month=models.Count(models.Q(
                        created_at__gte=(
                            timezone.now().replace(
                                day=1,
                                hour=0,
                                minute=0,
                                second=0,
                                microsecond=0
                            )
                        )
                    ))
                )

                if counts['hour'] >= push_limits[0]:
                    raise ValidationError(('Достигнут лимит по отправке PUSH '
                                           'уведомлений за последний час.'))

                elif counts['day'] >= push_limits[1]:
                    raise ValidationError(('Достигнут лимит по отправке PUSH '
                                           'уведомлений за текущий день.'))

                elif counts['month'] >= push_limits[2]:
                    raise ValidationError(('Достигнут лимит по отправке PUSH '
                                           'уведомлений за текущий месяц.'))

            if not self.is_send_immediately:
                if not self.send_at:
                    raise ValidationError({
                        'send_at': [
                            'Обязательное поле.'
                        ]
                    })
                elif self.send_at < timezone.now():
                    raise ValidationError({
                        'send_at': [
                            ('Дата и время отправки не может быть '
                                'меньше текущего.')
                        ]
                    })
            else:
                self.send_at = None

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_status_waiting(self):
        return self.status == self.Status.WAITING

    @property
    def is_status_processing(self):
        return self.status == self.Status.PROCESSING

    @property
    def is_status_completed(self):
        return self.status == self.Status.COMPLETED

    def get_status(self):
        return self.Status(self.status)

    def get_status_dict(self):
        return self.get_status().dict()

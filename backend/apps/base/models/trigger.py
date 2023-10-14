from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..fields import LimitedImageField
from ..managers import TriggerManager
from ..validators import check_if_the_wallet_has_been_deleted
from .audience import Audience
from .wallet import Wallet


class Trigger(models.Model):
    """
    Триггерные рассылки. Если активирован чекбокс 'Повышенный кешбек/скидка?'
    то так-же создаются записи в модели 'client/percent/IncreasedPercentage'.

    Сигналы: signals -> trigger
    """

    wallet = models.ForeignKey(
        Wallet,
        verbose_name='Карта',
        on_delete=models.PROTECT,
        related_name='triggers'
    )
    audience = models.ForeignKey(
        Audience,
        verbose_name='Аудитория',
        on_delete=models.PROTECT,
        related_name='triggers',
        null=True,
        blank=True
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=255
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=2048
    )
    icon = LimitedImageField(
        verbose_name='Иконка',
        upload_to='triggers/icons/%Y/%m/%d/',
        max_upload_size=1024,
        help_text=(
            'Допустимые форматы файла: png, jpg. '
            'Максимальный размер одного файла не более 1 Мб.'
        )
    )
    is_send_push_notifications = models.BooleanField(
        verbose_name='Отправить пуш уведомления?',
        default=False
    )
    message_for_push_notifications = models.TextField(
        verbose_name='Текст рассылки',
        max_length=2048,
        null=True,
        blank=True
    )
    is_add_bonuses = models.BooleanField(
        verbose_name='Начислить баллы?',
        default=False
    )
    bonuses = models.DecimalField(
        verbose_name='Кол-во баллов для начисления',
        default=0,
        max_digits=12,
        decimal_places=2,
        validators=(MinValueValidator(0),)
    )
    is_increased_percentage = models.BooleanField(
        verbose_name='Повышенный кешбек/скидка?',
        default=False
    )
    percent = models.PositiveSmallIntegerField(
        verbose_name='% Кэшбэка/Скидки',
        default=0,
        validators=(MinValueValidator(0), MaxValueValidator(100),),
        help_text='Минимальный процент: 0%, Максимальный процент: 100%.'
    )
    days_before_the_event = models.PositiveSmallIntegerField(
        verbose_name='Дней повышенного кэшбэка/скидки до события',
        default=0,
        validators=(MinValueValidator(0),)
    )
    days_after_the_event = models.PositiveSmallIntegerField(
        verbose_name='Дней повышенного кэшбэка/скидки после события',
        default=0,
        validators=(MinValueValidator(0),)
    )
    is_repeat_every_year = models.BooleanField(
        verbose_name='Повторять событие каждый год?',
        default=False
    )
    launch_at = models.DateTimeField(
        verbose_name='Дата и время запуска'
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата последнего обновления',
        auto_now=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    objects = TriggerManager()

    class Meta:
        verbose_name = 'Триггерная рассылка'
        verbose_name_plural = 'Триггерные рассылки'
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def clean(self):
        if hasattr(self, 'wallet') and self.wallet is not None:
            if not self.id:
                check_if_the_wallet_has_been_deleted(self.wallet)

            if hasattr(self, 'audience') and self.audience is not None:
                if self.wallet.id != self.audience.wallet.id:
                    raise ValidationError({
                        'audience': [
                            'Данная фильтрация не принадлежит выбранной карте.'
                        ]
                    })

            if self.is_add_bonuses and not self.wallet.is_type_bonus:
                raise ValidationError({
                    'is_add_bonuses': [
                        ('Тип карты не соответствует типу: '
                         f'{Wallet.Type.BONUS.label}')
                    ]
                })

        if self.is_send_push_notifications:
            if not self.message_for_push_notifications:
                raise ValidationError({
                    'message_for_push_notifications': [
                        'Обязательное поле.'
                    ]
                })

        if self.launch_at is not None:
            if self.launch_at.minute > 0 or self.launch_at.second > 0:
                raise ValidationError({
                    'launch_at': [
                        ('Триггерные рассылки можно запускать ровно в '
                            '00 мин. и 00 сек.')
                    ]
                })

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

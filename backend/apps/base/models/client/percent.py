from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class IncreasedPercentage(models.Model):
    client = models.ForeignKey(
        'base.Client',
        verbose_name='Клиент',
        on_delete=models.CASCADE,
        related_name='percentages'
    )
    trigger = models.ForeignKey(
        'base.Trigger',
        verbose_name='Триггерная рассылка',
        on_delete=models.CASCADE,
        related_name='percentages',
        null=True,
        blank=True
    )
    percent = models.PositiveSmallIntegerField(
        verbose_name='% Кэшбэка/Скидки',
        default=0,
        validators=(MinValueValidator(0), MaxValueValidator(100),),
        help_text='Минимальный процент: 0%, Максимальный процент: 100%.'
    )
    activated_at = models.DateField(
        verbose_name='Дата начала'
    )
    expires_at = models.DateField(
        verbose_name='Дата окончания'
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
        verbose_name = 'Повышенный процент'
        verbose_name_plural = 'Повышенные проценты'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.client.name} | {self.percent}%'

    def clean(self):
        if self.activated_at is not None and self.expires_at is not None:
            if self.activated_at > self.expires_at:
                raise ValidationError({
                    'activated_at': [
                        'Дата начала не может быть больше даты окончания.'
                    ]
                })
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
